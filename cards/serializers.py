from rest_framework import serializers
from .models import (
    CardCategory,
    CardListing,
    YugiohCard,
    YugiohCardImage,
    YugiohCardSet,
    YugiohCardTypeLine,
)

from django.db.models import Avg, Count, Min, Max, Q
from rest_framework import viewsets, filters




class YugiohCardImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = YugiohCardImage
        fields = ["id", "image_url", "image_url_small", "image_url_cropped"]


class YugiohCardTypeLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = YugiohCardTypeLine
        fields = ["id", "value"]


class YugiohCardSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = YugiohCardSet
        fields = ["id", "set_name", "set_code", "set_rarity", "set_rarity_code", "set_price"]


class YugiohCardSerializer(serializers.ModelSerializer):
    images = YugiohCardImageSerializer(many=True, read_only=True)
    typelines = YugiohCardTypeLineSerializer(many=True, read_only=True)
    sets = YugiohCardSetSerializer(many=True, read_only=True)
    main_image = serializers.SerializerMethodField()

    listing_count = serializers.IntegerField(read_only=True)
    avg_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = YugiohCard
        fields = [
            "id",
            "ygopro_id",
            "konami_id",
            "name",
            "slug",
            "card_type",
            "human_readable_card_type",
            "frame_type",
            "desc",
            "atk",
            "defense",
            "level",
            "race",
            "attribute",
            "archetype",
            "ygoprodeck_url",
            "is_featured",
            "main_image",
            "images",
            "typelines",
            "sets",
            "listing_count",
            "avg_price",
            "created_at",
            "updated_at",
        ]

    def get_main_image(self, obj):
        first_image = obj.images.first()
        return first_image.image_url if first_image else None


class CardCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CardCategory
        fields = "__all__"


class CardListingSerializer(serializers.ModelSerializer):
    seller_username = serializers.CharField(source="seller.username", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)
    yugioh_card_name = serializers.CharField(source="yugioh_card.name", read_only=True)
    yugioh_card_slug = serializers.CharField(source="yugioh_card.slug", read_only=True)
    yugioh_card_set_code = serializers.CharField(source="yugioh_card_set.set_code", read_only=True)

    seller_images = serializers.ListField(
        child=serializers.URLField(),
        required=False,
        allow_empty=True
    )

    class Meta:
        model = CardListing
        fields = [
            "id",
            "seller",
            "seller_username",
            "is_sold",

            "yugioh_card",
            "yugioh_card_name",
            "yugioh_card_slug",

            "yugioh_card_set",
            "yugioh_card_set_code",

            "category",
            "category_name",
            "name",
            "slug",
            "card_description",
            "seller_description",
            "archetype",
            "rarity",
            "card_type",
            "attribute",
            "set_name",
            "set_code",
            "condition",
            "edition",
            "language",
            "quantity",
            "price",
            "image_url",
            "seller_images",
            "is_active",
            "is_featured",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["seller","slug"]
        
class YugiohCardSerializer(serializers.ModelSerializer):
    images = YugiohCardImageSerializer(many=True, read_only=True)
    typelines = YugiohCardTypeLineSerializer(many=True, read_only=True)
    sets = YugiohCardSetSerializer(many=True, read_only=True)
    main_image = serializers.SerializerMethodField()

    listing_count = serializers.IntegerField(read_only=True)
    avg_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = YugiohCard
        fields = [
            "id",
            "ygopro_id",
            "konami_id",
            "name",
            "slug",
            "card_type",
            "human_readable_card_type",
            "frame_type",
            "desc",
            "atk",
            "defense",
            "level",
            "race",
            "attribute",
            "archetype",
            "ygoprodeck_url",
            "is_featured",
            "main_image",
            "images",
            "typelines",
            "sets",
            "listing_count",
            "avg_price",
            "created_at",
            "updated_at",
        ]

    def get_main_image(self, obj):
        first_image = obj.images.first()
        return first_image.image_url if first_image else None