from django.db import transaction
from rest_framework import serializers
from .models import Order, OrderItem,City
from cards.models import CardListing
from cards.services import refresh_featured_cards_last_7_days



class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ["id", "name", "shipping_price"]

class OrderItemSerializer(serializers.ModelSerializer):
    card_name = serializers.CharField(source="card.name", read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "card", "card_name", "quantity", "unit_price"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    listing = serializers.PrimaryKeyRelatedField(
        queryset=CardListing.objects.filter(is_active=True),
        write_only=True
    )
    quantity = serializers.IntegerField(write_only=True, default=1, min_value=1)

    class Meta:
        model = Order
        fields = [
            "id",
            "listing",
            "quantity",
            "full_name",
            "email",
            "phone",
            "address",
            "city",
            "notes",
            "payment_method",
            "payment_status",
            "is_paid",
            "total_price",
            "status",
            "items",
            "created_at",
        ]
        read_only_fields = [
            "email",
            "payment_status",
            "is_paid",
            "total_price",
            "status",
            "created_at",
        ]

    def validate(self, attrs):
      request = self.context["request"]
      listing = attrs.get("listing")
      quantity = attrs.get("quantity", 1)

      submitted_email = self.initial_data.get("email")

      if submitted_email and submitted_email.strip().lower() != request.user.email.strip().lower():
        raise serializers.ValidationError({
            "email": "You cannot use a different email from your account email."
        })

      if listing.seller == request.user:
        raise serializers.ValidationError({
            "listing": "You cannot buy your own listing."
        })

      if listing.is_sold:
        raise serializers.ValidationError({
            "listing": "This listing is already sold."
        })

      if listing.quantity < quantity:
        raise serializers.ValidationError({
            "quantity": "Requested quantity is not available."
        })

      return attrs

    @transaction.atomic
    def create(self, validated_data):
        listing = validated_data.pop("listing")
        quantity = validated_data.pop("quantity", 1)
        user = self.context["request"].user

        validated_data["email"] = user.email

        order = Order.objects.create(
            user=user,
            total_price=listing.price * quantity,
            payment_status="pending",
            is_paid=False,
            **validated_data,
        )

        OrderItem.objects.create(
            order=order,
            card=listing,
            quantity=quantity,
            unit_price=listing.price,
        )

        listing.quantity -= quantity

        if listing.quantity <= 0:
            listing.quantity = 0
            listing.is_sold = True

        listing.save()
        refresh_featured_cards_last_7_days()

        return order