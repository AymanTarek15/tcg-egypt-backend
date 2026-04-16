from rest_framework import serializers
from .models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    listing_id = serializers.IntegerField(source="listing.id", read_only=True)
    name = serializers.CharField(source="listing.name", read_only=True)
    slug = serializers.CharField(source="listing.slug", read_only=True)
    price = serializers.DecimalField(source="listing.price", max_digits=10, decimal_places=2, read_only=True)
    image = serializers.CharField(source="listing.image_url", read_only=True)
    seller_id = serializers.IntegerField(source="listing.seller.id", read_only=True)
    seller_username = serializers.CharField(source="listing.seller.username", read_only=True)
    is_sold = serializers.BooleanField(source="listing.is_sold", read_only=True)

    class Meta:
        model = CartItem
        fields = [
            "id",
            "listing_id",
            "name",
            "slug",
            "price",
            "image",
            "seller_id",
            "seller_username",
            "is_sold",
            "quantity",
        ]


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "items", "created_at", "updated_at"]