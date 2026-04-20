from django.conf import settings
from django.db import models
from django.utils import timezone


class UserPointWallet(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="point_wallet"
    )
    free_points_balance = models.PositiveIntegerField(default=0)
    paid_points_balance = models.PositiveIntegerField(default=0)

    free_points_monthly_quota = models.PositiveIntegerField(default=20)
    free_points_last_reset_at = models.DateTimeField(default=timezone.now)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} wallet"


class PointTransaction(models.Model):
    TRANSACTION_TYPES = [
        ("free_grant", "Free Grant"),
        ("free_reset", "Free Reset"),
        ("paid_purchase", "Paid Purchase"),
        ("usage_free", "Usage Free"),
        ("usage_paid", "Usage Paid"),
        ("manual_adjustment", "Manual Adjustment"),
        ("refund_paid", "Refund Paid"),
    ]

    wallet = models.ForeignKey(
        UserPointWallet,
        on_delete=models.CASCADE,
        related_name="transactions"
    )
    transaction_type = models.CharField(max_length=30, choices=TRANSACTION_TYPES)
    points = models.IntegerField()  # positive or negative
    description = models.CharField(max_length=255, blank=True, null=True)

    balance_free_after = models.PositiveIntegerField(default=0)
    balance_paid_after = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.wallet.user.username} - {self.transaction_type} - {self.points}"


class PointPackage(models.Model):
    name = models.CharField(max_length=100)
    points = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.points} points"


class PointPurchase(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
        ("cancelled", "Cancelled"),
        ("refunded", "Refunded"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="point_purchases"
    )
    package = models.ForeignKey(PointPackage, on_delete=models.PROTECT)
    points = models.PositiveIntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    provider = models.CharField(max_length=50, default="paymob")
    provider_reference = models.CharField(max_length=255, blank=True, null=True)
    intention_reference = models.CharField(max_length=255, blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    raw_response = models.JSONField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.package.name} - {self.status}"