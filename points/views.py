from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import generics, status

from .models import PointPackage, PointPurchase
from .serializers import (
    UserPointWalletSerializer,
    PointTransactionSerializer,
    PointPackageSerializer,
    PointPurchaseSerializer,
)
from .services import (
    get_or_create_wallet,
    create_paymob_point_purchase_intention,
    credit_paid_points,
)
from .utils import verify_paymob_hmac


class WalletView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        wallet = get_or_create_wallet(request.user)
        serializer = UserPointWalletSerializer(wallet)
        return Response(serializer.data)


class TransactionListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PointTransactionSerializer

    def get_queryset(self):
        wallet = get_or_create_wallet(self.request.user)
        return wallet.transactions.order_by("-created_at")


class PackageListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = PointPackageSerializer
    queryset = PointPackage.objects.filter(is_active=True).order_by("price")


class PurchaseListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PointPurchaseSerializer

    def get_queryset(self):
        return PointPurchase.objects.filter(user=self.request.user).order_by("-created_at")


class StartPointPurchaseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        package_id = request.data.get("package_id")
        package = PointPackage.objects.filter(id=package_id, is_active=True).first()

        if not package:
            return Response(
                {"detail": "Invalid package."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        purchase = PointPurchase.objects.create(
            user=request.user,
            package=package,
            points=package.points,
            amount=package.price,
            status="pending",
        )

        try:
            paymob_data = create_paymob_point_purchase_intention(
                purchase=purchase,
                user=request.user,
            )
        except Exception as e:
            purchase.status = "failed"
            purchase.raw_response = {"error": str(e)}
            purchase.save(update_fields=["status", "raw_response", "updated_at"])
            return Response(
                {"detail": f"Failed to create payment intention: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        purchase.provider_reference = paymob_data["merchant_order_id"]
        purchase.intention_reference = paymob_data["intention_reference"]
        purchase.raw_response = paymob_data["raw"]
        purchase.save(
            update_fields=[
                "provider_reference",
                "intention_reference",
                "raw_response",
                "updated_at",
            ]
        )

        return Response(
            {
                "checkout_url": paymob_data["checkout_url"],
                "purchase_id": purchase.id,
            },
            status=status.HTTP_200_OK,
        )


class PaymobPointWebhookView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        payload = request.data

        if not verify_paymob_hmac(payload):
            return Response({"detail": "Invalid HMAC"}, status=status.HTTP_400_BAD_REQUEST)

        obj = payload.get("obj", {})
        success = obj.get("success", False)

        merchant_order_id = (
            obj.get("order", {}).get("merchant_order_id")
            or obj.get("order", {}).get("merchant_order_id".lower())
            or obj.get("merchant_order_id")
        )

        if not merchant_order_id:
            return Response(
                {"detail": "Missing merchant_order_id"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not str(merchant_order_id).startswith("points_"):
            return Response(
                {"detail": "Invalid purchase reference"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        purchase_id = str(merchant_order_id).replace("points_", "", 1)

        purchase = PointPurchase.objects.filter(id=purchase_id).first()
        if not purchase:
            return Response(
                {"detail": "Purchase not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if purchase.status == "paid":
            return Response({"ok": True}, status=status.HTTP_200_OK)

        purchase.raw_response = payload

        if success:
            purchase.status = "paid"
            purchase.save(update_fields=["status", "raw_response", "updated_at"])

            credit_paid_points(
                user=purchase.user,
                points=purchase.points,
                description=f"Purchased package: {purchase.package.name}",
            )
        else:
            purchase.status = "failed"
            purchase.save(update_fields=["status", "raw_response", "updated_at"])

        return Response({"ok": True}, status=status.HTTP_200_OK)