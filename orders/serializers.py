from rest_framework import serializers
from .models import Order, OrderItem, City


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

    class Meta:
        model = Order
        fields = [
            "id",
            "seller",
            "full_name",
            "email",
            "phone",
            "address",
            "city",
            "notes",
            "payment_method",
            "payment_status",
            "is_paid",
            "subtotal",
            "shipping_cost",
            "total_price",
            "status",
            "items",
            "created_at",
        ]
        read_only_fields = [
            "seller",
            "email",
            "payment_status",
            "is_paid",
            "subtotal",
            "shipping_cost",
            "total_price",
            "status",
            "items",
            "created_at",
        ]