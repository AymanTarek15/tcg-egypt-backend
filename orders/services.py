from collections import defaultdict
from decimal import Decimal

from django.db import transaction

from cart.models import Cart
from .models import Order, OrderItem, City
from cards.services import refresh_featured_cards_last_7_days

MINIMUM_ORDER_PER_SELLER = Decimal("250.00")


def group_cart_items_by_seller(cart_items):
    grouped = defaultdict(list)

    for item in cart_items:
        seller = item.listing.seller
        grouped[seller].append(item)

    return grouped


@transaction.atomic
def create_orders_from_cart(user, checkout_data):
    try:
        cart = Cart.objects.prefetch_related(
            "items",
            "items__listing",
            "items__listing__seller"
        ).get(user=user)
    except Cart.DoesNotExist:
        raise ValueError("Cart not found")

    cart_items = cart.items.all()

    if not cart_items.exists():
        raise ValueError("Your cart is empty")

    full_name = checkout_data.get("full_name", "").strip()
    phone = checkout_data.get("phone", "").strip()
    address = checkout_data.get("address", "").strip()
    city_name = checkout_data.get("city", "").strip()
    notes = checkout_data.get("notes", "").strip()
    payment_method = checkout_data.get("payment_method", "cash_on_delivery")

    if not full_name:
        raise ValueError("Full name is required")

    if not phone:
        raise ValueError("Phone is required")

    if not address:
        raise ValueError("Address is required")

    if not city_name:
        raise ValueError("City is required")

    try:
        city_obj = City.objects.get(name__iexact=city_name, is_active=True)
    except City.DoesNotExist:
        raise ValueError("Selected city is invalid")

    shipping_cost = city_obj.shipping_price

    grouped = group_cart_items_by_seller(cart_items)
    created_orders = []

    for seller, items in grouped.items():
        subtotal = sum(
            Decimal(item.listing.price) * item.quantity
            for item in items
        )

        if subtotal < MINIMUM_ORDER_PER_SELLER:
            raise ValueError(
                f"Minimum order for seller {seller.username} is {MINIMUM_ORDER_PER_SELLER} EGP"
            )

        order = Order.objects.create(
            user=user,
            seller=seller,
            subtotal=subtotal,
            shipping_cost=shipping_cost,
            total_price=subtotal + shipping_cost,
            payment_method=payment_method,
            payment_status="pending",
            is_paid=False,
            status="pending",
            full_name=full_name,
            phone=phone,
            email=user.email,   # force account email
            address=address,
            city=city_obj.name, # because Order.city is CharField
            notes=notes,
        )

        for item in items:
            listing = item.listing

            if listing.seller == user:
                raise ValueError(f"You cannot buy your own listing: {listing.name}")

            if listing.is_sold:
                raise ValueError(f"{listing.name} is already sold")

            if listing.quantity < item.quantity:
                raise ValueError(
                    f"Requested quantity is not available for {listing.name}"
                )

            OrderItem.objects.create(
                order=order,
                card=listing,
                quantity=item.quantity,
                unit_price=listing.price,
            )

            listing.quantity -= item.quantity

            if listing.quantity <= 0:
                listing.quantity = 0
                listing.is_sold = True

            listing.save()

        created_orders.append(order)

    cart.items.all().delete()
    refresh_featured_cards_last_7_days()

    return created_orders