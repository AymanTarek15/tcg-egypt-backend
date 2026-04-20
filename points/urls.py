from django.urls import path
from .views import (
    WalletView,
    TransactionListView,
    PackageListView,
    PurchaseListView,
    StartPointPurchaseView,
    PaymobPointWebhookView,
)

urlpatterns = [
    path("wallet/", WalletView.as_view(), name="points-wallet"),
    path("transactions/", TransactionListView.as_view(), name="points-transactions"),
    path("packages/", PackageListView.as_view(), name="points-packages"),
    path("purchases/", PurchaseListView.as_view(), name="points-purchases"),
    path("purchase/start/", StartPointPurchaseView.as_view(), name="points-purchase-start"),
    path("purchase/start/", StartPointPurchaseView.as_view(), name="points-purchase-start"),
    path("paymob/webhook/", PaymobPointWebhookView.as_view(), name="paymob-webhook"),
]