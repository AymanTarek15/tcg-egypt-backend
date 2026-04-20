from django.contrib import admin
from .models import UserPointWallet, PointTransaction, PointPackage, PointPurchase


@admin.register(UserPointWallet)
class UserPointWalletAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "free_points_balance",
        "paid_points_balance",
        "free_points_monthly_quota",
        "free_points_last_reset_at",
    )
    search_fields = ("user__username", "user__email")


@admin.register(PointTransaction)
class PointTransactionAdmin(admin.ModelAdmin):
    list_display = (
        "wallet",
        "transaction_type",
        "points",
        "created_at",
    )
    search_fields = ("wallet__user__username", "wallet__user__email")
    list_filter = ("transaction_type", "created_at")


@admin.register(PointPackage)
class PointPackageAdmin(admin.ModelAdmin):
    list_display = ("name", "points", "price", "is_active")
    list_filter = ("is_active",)


@admin.register(PointPurchase)
class PointPurchaseAdmin(admin.ModelAdmin):
    list_display = ("user", "package", "points", "amount", "status", "created_at")
    search_fields = ("user__username", "user__email")
    list_filter = ("status", "created_at")