from django.db import models
from django.conf import settings
from django.utils.text import slugify


class YugiohCard(models.Model):
    ygopro_id = models.BigIntegerField(unique=True)
    konami_id = models.BigIntegerField(blank=True, null=True)

    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)

    card_type = models.CharField(max_length=150, blank=True)
    human_readable_card_type = models.CharField(max_length=150, blank=True)
    frame_type = models.CharField(max_length=150, blank=True)
    desc = models.TextField(blank=True)

    atk = models.IntegerField(blank=True, null=True)
    defense = models.IntegerField(blank=True, null=True)
    level = models.IntegerField(blank=True, null=True)
    race = models.CharField(max_length=150, blank=True)
    attribute = models.CharField(max_length=100, blank=True)
    archetype = models.CharField(max_length=200, blank=True)

    ygoprodeck_url = models.URLField(blank=True)
    is_featured = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class YugiohCardImage(models.Model):
    card = models.ForeignKey(
        YugiohCard,
        on_delete=models.CASCADE,
        related_name="images"
    )
    image_url = models.URLField()
    image_url_small = models.URLField(blank=True)
    image_url_cropped = models.URLField(blank=True)

    def __str__(self):
        return f"{self.card.name} image"


class YugiohCardTypeLine(models.Model):
    card = models.ForeignKey(
        YugiohCard,
        on_delete=models.CASCADE,
        related_name="typelines"
    )
    value = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.card.name} - {self.value}"


class YugiohCardSet(models.Model):
    card = models.ForeignKey(
        YugiohCard,
        on_delete=models.CASCADE,
        related_name="sets"
    )
    set_name = models.CharField(max_length=255)
    set_code = models.CharField(max_length=100)
    set_rarity = models.CharField(max_length=150, blank=True)
    set_rarity_code = models.CharField(max_length=50, blank=True)
    set_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["card", "set_code", "set_rarity"],
                name="unique_card_version"
            )
        ]


class CardCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class CardListing(models.Model):
    CONDITION_CHOICES = [
        ("mint", "Mint"),
        ("near_mint", "Near Mint"),
        ("light_played", "Light Played"),
        ("moderate_played", "Moderate Played"),
        ("heavy_played", "Heavy Played"),
        ("damaged", "Damaged"),
    ]
    
    # id=models.AutoField(primary_key=True)
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="card_listings")

    yugioh_card = models.ForeignKey(
        "YugiohCard",
        on_delete=models.CASCADE,
        related_name="listings"
    )
    yugioh_card_set = models.ForeignKey(
        "YugiohCardSet",
        on_delete=models.CASCADE,
        related_name="listings"
    )

    category = models.ForeignKey(
        CardCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cards"
    )

    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    card_description = models.TextField(blank=True)
    seller_description = models.TextField(blank=True)

    archetype = models.CharField(max_length=100, blank=True)
    rarity = models.CharField(max_length=100, blank=True)
    card_type = models.CharField(max_length=50, blank=True)
    attribute = models.CharField(max_length=50, blank=True)

    set_name = models.CharField(max_length=150, blank=True)
    set_code = models.CharField(max_length=50, blank=True)

    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default="near_mint")
    edition = models.CharField(max_length=50, blank=True)
    language = models.CharField(max_length=50, default="English")
    quantity = models.PositiveIntegerField(default=1)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.URLField(blank=True)
    seller_images = models.JSONField(default=list, blank=True)

    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_sold = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.yugioh_card_set_id:
            self.yugioh_card = self.yugioh_card_set.card
            self.name = self.yugioh_card.name
            self.card_description = self.yugioh_card.desc
            self.archetype = self.yugioh_card.archetype
            self.card_type = self.yugioh_card.card_type
            self.attribute = self.yugioh_card.attribute

            self.set_name = self.yugioh_card_set.set_name
            self.set_code = self.yugioh_card_set.set_code
            self.rarity = self.yugioh_card_set.set_rarity

            first_image = self.yugioh_card.images.first()
            if first_image and not self.image_url:
                self.image_url = first_image.image_url

        if not self.slug:
            base_slug = slugify(f"{self.name}-{self.set_code}")

            if self.seller_id:
                base_slug = slugify(f"{self.name}-{self.set_code}-{self.seller_id}")

            slug = base_slug
            counter = 2

            while CardListing.objects.exclude(pk=self.pk).filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name