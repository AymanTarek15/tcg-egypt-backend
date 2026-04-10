from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum

from orders.models import OrderItem
from cards.models import YugiohCard


def refresh_featured_cards_last_7_days():
    since = timezone.now() - timedelta(days=7)

    top_cards = (
        OrderItem.objects.filter(
            order__created_at__gte=since,
            card__yugioh_card__isnull=False,
        )
        .values("card__yugioh_card")
        .annotate(total_purchased=Sum("quantity"))
        .order_by("-total_purchased")[:6]
    )

    top_card_ids = [item["card__yugioh_card"] for item in top_cards]

    YugiohCard.objects.update(is_featured=False)

    if top_card_ids:
        YugiohCard.objects.filter(id__in=top_card_ids).update(is_featured=True)