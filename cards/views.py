from django.db.models import Avg, Count, Max, Min, Q
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .utils import send_listing_created_email
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .permissions import IsSellerOrReadOnly

from django.conf import settings
from django.db import transaction
from points.services import consume_points


from .models import CardCategory, CardListing, YugiohCard, YugiohCardSet
from .serializers import (
    CardCategorySerializer,
    CardListingSerializer,
    YugiohCardSerializer,
    YugiohCardSetSerializer,
)


class CardCategoryViewSet(viewsets.ModelViewSet):
    queryset = CardCategory.objects.all()
    serializer_class = CardCategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class CardListingViewSet(viewsets.ModelViewSet):
    serializer_class = CardListingSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsSellerOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        "id",
        "name",
        "card_description",
        "seller_description",
        "archetype",
        "rarity",
        "card_type",
        "attribute",
        "set_name",
        "set_code",
        "language",
        "edition",
        "category__name",
        "category__slug",
        "seller__username",
        "yugioh_card__name",
        "yugioh_card_set__set_name",
        "yugioh_card_set__set_code",
    ]
    ordering_fields = ["price", "created_at", "updated_at", "name", "quantity"]
    ordering = ["-created_at"]
    lookup_field = "slug"

    def get_queryset(self):
        queryset = (
            CardListing.objects.select_related(
                "seller",
                "category",
                "yugioh_card",
                "yugioh_card_set",
            )
            .filter(is_active=True)
        )

        is_sold = self.request.query_params.get("is_sold")
        if is_sold is not None:
            if is_sold.lower() == "true":
                queryset = queryset.filter(is_sold=True)
            elif is_sold.lower() == "false":
                queryset = queryset.filter(is_sold=False)

        slug = self.request.query_params.get("slug")
        if slug:
            queryset = queryset.filter(slug__iexact=slug)

        category = self.request.query_params.get("category")
        rarity = self.request.query_params.get("rarity")
        condition = self.request.query_params.get("condition")
        archetype = self.request.query_params.get("archetype")
        name = self.request.query_params.get("name")
        is_featured = self.request.query_params.get("is_featured")
        min_price = self.request.query_params.get("min_price")
        max_price = self.request.query_params.get("max_price")
        set_code = self.request.query_params.get("set_code")
        set_name = self.request.query_params.get("set_name")
        language = self.request.query_params.get("language")
        edition = self.request.query_params.get("edition")
        card_type = self.request.query_params.get("card_type")
        attribute = self.request.query_params.get("attribute")
        seller = self.request.query_params.get("seller")
        in_stock = self.request.query_params.get("in_stock")
        yugioh_card = self.request.query_params.get("yugioh_card")
        yugioh_card_set = self.request.query_params.get("yugioh_card_set")

        if category:
            queryset = queryset.filter(category__slug__iexact=category)

        if rarity:
            queryset = queryset.filter(rarity__iexact=rarity)

        if condition:
            queryset = queryset.filter(condition__iexact=condition)

        if archetype:
            queryset = queryset.filter(archetype__icontains=archetype)

        if name:
            queryset = queryset.filter(name__icontains=name)

        if set_code:
            queryset = queryset.filter(set_code__iexact=set_code)

        if set_name:
            queryset = queryset.filter(set_name__icontains=set_name)

        if language:
            queryset = queryset.filter(language__iexact=language)

        if edition:
            queryset = queryset.filter(edition__iexact=edition)

        if card_type:
            queryset = queryset.filter(card_type__iexact=card_type)

        if attribute:
            queryset = queryset.filter(attribute__iexact=attribute)

        if seller:
            queryset = queryset.filter(seller__username__iexact=seller)

        if yugioh_card:
            queryset = queryset.filter(yugioh_card_id=yugioh_card)

        if yugioh_card_set:
            queryset = queryset.filter(yugioh_card_set_id=yugioh_card_set)

        if is_featured is not None:
            if is_featured.lower() == "true":
                queryset = queryset.filter(is_featured=True)
            elif is_featured.lower() == "false":
                queryset = queryset.filter(is_featured=False)

        if in_stock is not None:
            if in_stock.lower() == "true":
                queryset = queryset.filter(quantity__gt=0)
            elif in_stock.lower() == "false":
                queryset = queryset.filter(quantity__lte=0)

        if min_price:
            queryset = queryset.filter(price__gte=min_price)

        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        return queryset

    def perform_create(self, serializer):
      with transaction.atomic():
        listing = serializer.save(seller=self.request.user)

        consume_points(
            user=self.request.user,
            required_points=settings.LISTING_POINT_COST,
            description=f"Created listing: {listing.name}"
        )


class YugiohCardViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = YugiohCardSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "archetype", "race", "attribute", "card_type"]
    ordering_fields = [
        "name",
        "atk",
        "level",
        "created_at",
        "listing_count",
        "avg_price",
        "min_price",
        "max_price",
    ]
    ordering = ["name"]
    lookup_field = "slug"

    def get_queryset(self):
        queryset = (
            YugiohCard.objects
            .prefetch_related("images", "typelines", "sets")
            .annotate(
                listing_count=Count(
                    "listings",
                    filter=Q(listings__is_active=True)
                ),
                avg_price=Avg(
                    "listings__price",
                    filter=Q(listings__is_active=True)
                ),
                min_price=Min(
                    "listings__price",
                    filter=Q(listings__is_active=True)
                ),
                max_price=Max(
                    "listings__price",
                    filter=Q(listings__is_active=True)
                ),
            )
            .order_by("name")
        )

        name = self.request.query_params.get("name")
        archetype = self.request.query_params.get("archetype")
        race = self.request.query_params.get("race")
        attribute = self.request.query_params.get("attribute")
        card_type = self.request.query_params.get("card_type")
        is_featured = self.request.query_params.get("is_featured")

        if name:
            queryset = queryset.filter(name__icontains=name)

        if archetype:
            queryset = queryset.filter(archetype__icontains=archetype)

        if race:
            queryset = queryset.filter(race__iexact=race)

        if attribute:
            queryset = queryset.filter(attribute__iexact=attribute)

        if card_type:
            queryset = queryset.filter(card_type__icontains=card_type)

        if is_featured is not None:
            if is_featured.lower() == "true":
                queryset = queryset.filter(is_featured=True)
            elif is_featured.lower() == "false":
                queryset = queryset.filter(is_featured=False)

        return queryset


class YugiohCardSetViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = YugiohCardSetSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["set_name", "set_code", "set_rarity", "card__name"]
    ordering_fields = [
        "set_name",
        "set_code",
        "set_price",
        "active_listing_count",
        "avg_listing_price",
        "min_listing_price",
        "max_listing_price",
    ]
    ordering = ["set_name"]

    def get_queryset(self):
        queryset = (
            YugiohCardSet.objects.select_related("card")
            .annotate(
                active_listing_count=Count(
                    "listings",
                    filter=Q(listings__is_active=True)
                ),
                avg_listing_price=Avg(
                    "listings__price",
                    filter=Q(listings__is_active=True)
                ),
                min_listing_price=Min(
                    "listings__price",
                    filter=Q(listings__is_active=True)
                ),
                max_listing_price=Max(
                    "listings__price",
                    filter=Q(listings__is_active=True)
                ),
            )
        )

        card = self.request.query_params.get("card")
        set_code = self.request.query_params.get("set_code")
        set_name = self.request.query_params.get("set_name")
        set_rarity = self.request.query_params.get("set_rarity")
        is_listed = self.request.query_params.get("is_listed")

        if card:
            queryset = queryset.filter(card__slug__iexact=card)

        if set_code:
            queryset = queryset.filter(set_code__iexact=set_code)

        if set_name:
            queryset = queryset.filter(set_name__icontains=set_name)

        if set_rarity:
            queryset = queryset.filter(set_rarity__iexact=set_rarity)

        if is_listed is not None:
            if is_listed.lower() == "true":
                queryset = queryset.filter(active_listing_count__gt=0)
            elif is_listed.lower() == "false":
                queryset = queryset.filter(active_listing_count=0)

        return queryset