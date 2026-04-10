from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, CityViewSet

router = DefaultRouter()
router.register("cities", CityViewSet, basename="cities")
router.register("", OrderViewSet, basename="orders")

urlpatterns = router.urls