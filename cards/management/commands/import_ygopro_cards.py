import requests
from decimal import Decimal, InvalidOperation

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from cards.models import (
    YugiohCard,
    YugiohCardImage,
    YugiohCardSet,
    YugiohCardTypeLine,
)


API_URL = "https://db.ygoprodeck.com/api/v7/cardinfo.php"


def clean_str(value, max_length=None):
    if value is None:
        value = ""
    else:
        value = str(value)

    if max_length is not None:
        return value[:max_length]
    return value


class Command(BaseCommand):
    help = "Import all Yu-Gi-Oh cards from YGOPRODeck"

    def handle(self, *args, **options):
        self.stdout.write("Fetching cards from YGOPRODeck...")

        response = requests.get(API_URL, timeout=120)
        response.raise_for_status()

        payload = response.json()
        cards = payload.get("data", [])

        created_count = 0
        updated_count = 0
        image_count = 0
        set_count = 0
        typeline_count = 0

        for card in cards:
            ygopro_id = card.get("id")
            name = clean_str(card.get("name")).strip()

            if not ygopro_id or not name:
                continue

            slug = slugify(name)[:255]
            original_slug = slug
            counter = 2

            while YugiohCard.objects.exclude(ygopro_id=ygopro_id).filter(slug=slug).exists():
                suffix = f"-{counter}"
                slug = f"{original_slug[:255 - len(suffix)]}{suffix}"
                counter += 1

            misc_info = card.get("misc_info") or []
            konami_id = misc_info[0].get("konami_id") if misc_info else None

            obj, created = YugiohCard.objects.update_or_create(
                ygopro_id=ygopro_id,
                defaults={
                    "konami_id": konami_id,
                    "name": name,
                    "slug": slug,
                    "card_type": clean_str(card.get("type"), 150),
                    "human_readable_card_type": clean_str(card.get("humanReadableCardType"), 150),
                    "frame_type": clean_str(card.get("frameType"), 150),
                    "desc": clean_str(card.get("desc")),
                    "atk": card.get("atk"),
                    "defense": card.get("def"),
                    "level": card.get("level"),
                    "race": clean_str(card.get("race"), 150),
                    "attribute": clean_str(card.get("attribute"), 100),
                    "archetype": clean_str(card.get("archetype"), 200),
                    "ygoprodeck_url": clean_str(card.get("ygoprodeck_url")),
                },
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

            obj.images.all().delete()
            obj.sets.all().delete()
            obj.typelines.all().delete()

            for img in card.get("card_images") or []:
                YugiohCardImage.objects.create(
                    card=obj,
                    image_url=clean_str(img.get("image_url")),
                    image_url_small=clean_str(img.get("image_url_small")),
                    image_url_cropped=clean_str(img.get("image_url_cropped")),
                )
                image_count += 1

            for line in card.get("typeline") or []:
                YugiohCardTypeLine.objects.create(
                    card=obj,
                    value=clean_str(line, 100),
                )
                typeline_count += 1

            for s in card.get("card_sets") or []:
                raw_price = s.get("set_price")
                price_value = None

                if raw_price not in (None, ""):
                    try:
                        price_value = Decimal(str(raw_price))
                    except (InvalidOperation, ValueError):
                        price_value = None

                YugiohCardSet.objects.create(
                    card=obj,
                    set_name=clean_str(s.get("set_name"), 255),
                    set_code=clean_str(s.get("set_code"), 100),
                    set_rarity=clean_str(s.get("set_rarity"), 150),
                    set_rarity_code=clean_str(s.get("set_rarity_code"), 50),
                    set_price=price_value,
                )
                set_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Created: {created_count}, Updated: {updated_count}, "
                f"Images: {image_count}, TypeLines: {typeline_count}, Sets: {set_count}"
            )
        )