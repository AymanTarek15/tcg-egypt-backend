from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .models import Order, City
from .serializers import OrderSerializer, CitySerializer
from .emails import (
    send_buyer_order_confirmation,
    send_seller_card_sold_email,
)


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
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()

        try:
            send_buyer_order_confirmation(order)
        except Exception as e:
            print("Buyer email failed:", str(e))

        try:
            send_seller_card_sold_email(order)
        except Exception as e:
            print("Seller email failed:", str(e))

        if order.payment_method == "card":
            return Response(
                {
                    "message": "Order created. Card payment session should be created here.",
                    "order_id": order.id,
                    "payment_method": order.payment_method,
                    "payment_status": order.payment_status,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            self.get_serializer(order).data,
            status=status.HTTP_201_CREATED
        )