from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError
import requests
from django.conf import settings
from .models import UserPointWallet, PointTransaction


def get_or_create_wallet(user):
    wallet, created = UserPointWallet.objects.get_or_create(
        user=user,
        defaults={
            "free_points_balance": 20,
            "paid_points_balance": 0,
            "free_points_monthly_quota": 20,
            "free_points_last_reset_at": timezone.now(),
        }
    )

    if created:
        PointTransaction.objects.create(
            wallet=wallet,
            transaction_type="free_grant",
            points=wallet.free_points_balance,
            description="Initial free points",
            balance_free_after=wallet.free_points_balance,
            balance_paid_after=wallet.paid_points_balance,
        )

    return wallet


@transaction.atomic
def consume_points(wallet, required_points, description="Point usage"):
    total_available = wallet.free_points_balance + wallet.paid_points_balance
    if total_available < required_points:
        raise ValidationError("Not enough points.")

    remaining = required_points

    if wallet.free_points_balance > 0:
        free_used = min(wallet.free_points_balance, remaining)
        wallet.free_points_balance -= free_used
        remaining -= free_used

        PointTransaction.objects.create(
            wallet=wallet,
            transaction_type="usage_free",
            points=-free_used,
            description=description,
            balance_free_after=wallet.free_points_balance,
            balance_paid_after=wallet.paid_points_balance,
        )

    if remaining > 0:
        paid_used = min(wallet.paid_points_balance, remaining)
        wallet.paid_points_balance -= paid_used
        remaining -= paid_used

        PointTransaction.objects.create(
            wallet=wallet,
            transaction_type="usage_paid",
            points=-paid_used,
            description=description,
            balance_free_after=wallet.free_points_balance,
            balance_paid_after=wallet.paid_points_balance,
        )

    wallet.save(update_fields=["free_points_balance", "paid_points_balance", "updated_at"])
    return wallet


@transaction.atomic
def credit_paid_points(user, points, description="Paid points purchase"):
    wallet = get_or_create_wallet(user)

    wallet.paid_points_balance += points
    wallet.save(update_fields=["paid_points_balance", "updated_at"])

    PointTransaction.objects.create(
        wallet=wallet,
        transaction_type="paid_purchase",
        points=points,
        description=description,
        balance_free_after=wallet.free_points_balance,
        balance_paid_after=wallet.paid_points_balance,
    )

    return wallet


@transaction.atomic
def reset_wallet_free_points(wallet):
    wallet.free_points_balance = wallet.free_points_monthly_quota
    wallet.free_points_last_reset_at = timezone.now()
    wallet.save(update_fields=[
        "free_points_balance",
        "free_points_last_reset_at",
        "updated_at"
    ])

    PointTransaction.objects.create(
        wallet=wallet,
        transaction_type="free_reset",
        points=wallet.free_points_monthly_quota,
        description="Monthly free points reset",
        balance_free_after=wallet.free_points_balance,
        balance_paid_after=wallet.paid_points_balance,
    )


def reset_all_wallets_free_points():
    wallets = UserPointWallet.objects.select_related("user").all()
    for wallet in wallets:
        reset_wallet_free_points(wallet)
        
        
        
        
        


def create_paymob_point_purchase_intention(purchase, user):
    payload = {
        # Fill using the exact fields required by your Paymob account setup
        # amount, currency, merchant_order_id, allowed payment methods, billing data, etc.
    }

    headers = {
        "Authorization": f"Token {settings.PAYMOB_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    response = requests.post(
        settings.PAYMOB_INTENTION_URL,
        json=payload,
        headers=headers,
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()

    return {
        **data,
        "merchant_order_id": f"points_{purchase.id}",
        "checkout_url": data.get("payment_keys", {}).get("hosted_url") or data.get("checkout_url"),
    }
    
    
    
import requests
from django.conf import settings

from .models import PointPurchase


def create_paymob_point_purchase_intention(purchase, user):
    merchant_order_id = f"points_{purchase.id}"

    payload = {
        "amount": float(purchase.amount),
        "currency": "EGP",
        "payment_methods": [int(settings.PAYMOB_CARD_INTEGRATION_ID)],
        "items": [
            {
                "name": purchase.package.name,
                "amount": float(purchase.amount),
                "description": f"{purchase.points} paid points",
                "quantity": 1,
            }
        ],
        "billing_data": {
            "first_name": user.first_name or user.username or "User",
            "last_name": user.last_name or "User",
            "email": user.email,
            "phone_number": getattr(user, "phone_number", "") or "NA",
        },
        "special_reference": merchant_order_id,
        "notification_url": "https://api.tcg-egypt.com/api/points/paymob/webhook/",
        "redirection_url": settings.PAYMOB_SUCCESS_URL,
    }

    headers = {
        "Authorization": f"Token {settings.PAYMOB_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    response = requests.post(
        "https://accept.paymob.com/v1/intention/",
        json=payload,
        headers=headers,
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()

    client_secret = data.get("client_secret")
    if not client_secret:
        raise ValueError("Paymob did not return client_secret.")

    checkout_url = f"https://accept.paymob.com/unifiedcheckout/?publicKey={settings.PAYMOB_PUBLIC_KEY}&clientSecret={client_secret}"

    return {
        "raw": data,
        "checkout_url": checkout_url,
        "merchant_order_id": merchant_order_id,
        "intention_reference": str(data.get("id") or client_secret),
    }