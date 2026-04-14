from decimal import Decimal, ROUND_HALF_UP
from django.conf import settings
from django.core.mail import send_mail


def send_listing_created_email(listing):
    seller = listing.seller
    if not seller or not seller.email:
        return

    price = Decimal(str(listing.price or 0))

    commission_rate = Decimal("0.10")
    max_commission = Decimal("250.00")

    raw_commission = price * commission_rate

    # 🔥 APPLY CAP
    commission_amount = min(raw_commission, max_commission).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )

    seller_amount = (price - commission_amount).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )

    listing_url = f"{settings.FRONTEND_URL}/listings/{listing.slug}"

    subject = f"Your card listing is now live: {listing.name}"

    message = f"""
Hello {seller.username},

Your card has been listed successfully on TCG Egypt.

Listing details:
- Card: {listing.name}
- Set Name: {listing.set_name or 'N/A'}
- Set Code: {listing.set_code or 'N/A'}
- Rarity: {listing.rarity or 'N/A'}
- Condition: {listing.condition or 'N/A'}
- Listed Price: {price} EGP
- Listing URL: {listing_url}

Commission details:
- Marketplace commission: 10% (max 250 EGP)
- Commission charged: {commission_amount} EGP
- Amount you will receive: {seller_amount} EGP

Thank you for listing with TCG Egypt.
""".strip()

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[seller.email],
        fail_silently=False,
    )