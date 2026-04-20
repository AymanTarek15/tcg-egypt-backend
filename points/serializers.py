from rest_framework import serializers
from .models import UserPointWallet, PointTransaction, PointPackage, PointPurchase


class UserPointWalletSerializer(serializers.ModelSerializer):
    total_points = serializers.SerializerMethodField()

    class Meta:
        model = UserPointWallet
        fields = [
            "free_points_balance",
            "paid_points_balance",
            "free_points_monthly_quota",
            "free_points_last_reset_at",
            "total_points",
        ]

    def get_total_points(self, obj):
        return obj.free_points_balance + obj.paid_points_balance


class PointTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PointTransaction
        fields = [
            "id",
            "transaction_type",
            "points",
            "description",
            "balance_free_after",
            "balance_paid_after",
            "created_at",
        ]


class PointPackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PointPackage
        fields = ["id", "name", "points", "price"]


class PointPurchaseSerializer(serializers.ModelSerializer):
    package_name = serializers.CharField(source="package.name", read_only=True)

    class Meta:
        model = PointPurchase
        fields = [
            "id",
            "package",
            "package_name",
            "points",
            "amount",
            "status",
            "created_at",
        ]