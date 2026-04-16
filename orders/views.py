from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .models import Order, City
from .serializers import OrderSerializer, CitySerializer
from .emails import (
    send_buyer_order_confirmation,
    send_seller_card_sold_email,
)
from .services import create_orders_from_cart


class CityViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CitySerializer
    permission_classes = [AllowAny]
    queryset = City.objects.filter(is_active=True).order_by("name")


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Order.objects
            .filter(user=self.request.user)
            .prefetch_related("items", "items__card")
            .order_by("-created_at")
        )

    def create(self, request, *args, **kwargs):
        try:
            orders = create_orders_from_cart(
                user=request.user,
                checkout_data=request.data
            )

            for order in orders:
                try:
                    send_buyer_order_confirmation(order)
                except Exception as e:
                    print("Buyer email failed:", str(e))

                try:
                    send_seller_card_sold_email(order)
                except Exception as e:
                    print("Seller email failed:", str(e))

            serialized_orders = self.get_serializer(orders, many=True).data

            return Response(
                {
                    "message": "Orders created successfully",
                    "count": len(orders),
                    "orders": serialized_orders,
                },
                status=status.HTTP_201_CREATED,
            )

        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )