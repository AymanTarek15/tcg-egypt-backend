from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


def send_buyer_order_confirmation(order):
    subject = f"Order Confirmation #{order.id}"
    to_email = order.email

    context = {
        "order": order,
        "items": order.items.all(),
        "user": order.user,
    }

    text_body = render_to_string("emails/order_confirmation.txt", context)
    html_body = render_to_string("emails/order_confirmation.html", context)

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[to_email],
    )
    msg.attach_alternative(html_body, "text/html")
    msg.send(fail_silently=False)


def send_seller_card_sold_email(order):
    first_item = order.items.select_related("card", "card__seller").first()
    if not first_item or not first_item.card or not first_item.card.seller:
        return

    seller = first_item.card.seller
    seller_email = seller.email

    if not seller_email:
        return

    subject = f"Your card has been sold - Order #{order.id}"

    context = {
        "order": order,
        "item": first_item,
        "seller": seller,
        "buyer": order.user,
    }

    text_body = render_to_string("emails/card_sold_seller.txt", context)
    html_body = render_to_string("emails/card_sold_seller.html", context)

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[seller_email],
    )
    msg.attach_alternative(html_body, "text/html")
    msg.send(fail_silently=False)