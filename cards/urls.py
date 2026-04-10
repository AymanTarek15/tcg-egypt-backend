from rest_framework.routers import DefaultRouter
from .views import CardCategoryViewSet, CardListingViewSet,YugiohCardViewSet,YugiohCardSetViewSet

router = DefaultRouter()
router.register("categories", CardCategoryViewSet, basename="categories")
router.register("listings", CardListingViewSet, basename="listings")
router.register("database", YugiohCardViewSet, basename="yugioh-database")
router.register("sets", YugiohCardSetViewSet, basename="yugioh-card-sets")

urlpatterns = router.urls