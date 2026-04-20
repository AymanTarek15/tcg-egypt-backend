from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import Cart, CartItem
from .serializers import CartSerializer
from cards.models import CardListing


class CartDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)


class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        listing_id = request.data.get("listing_id")

        if not listing_id:
            return Response(
                {"error": "listing_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            listing = CardListing.objects.get(id=listing_id, is_active=True)
        except CardListing.DoesNotExist:
            return Response(
                {"error": "Listing not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if listing.seller == request.user:
            return Response(
                {"error": "You cannot add your own listing to cart"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if listing.is_sold:
            return Response(
                {"error": "This listing is already sold"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cart, _ = Cart.objects.get_or_create(user=request.user)

        already_in_cart = CartItem.objects.filter(
            cart=cart,
            listing=listing
        ).exists()

        if already_in_cart:
            return Response(
                {"error": "This card is already in your cart"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        CartItem.objects.create(
            cart=cart,
            listing=listing,
            quantity=1,
        )

        return Response(
            {"message": "Added to cart successfully"},
            status=status.HTTP_201_CREATED,
        )


class UpdateCartItemView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, item_id):
        quantity = int(request.data.get("quantity", 1))

        try:
            cart = request.user.cart
            item = cart.items.get(id=item_id)
        except (Cart.DoesNotExist, CartItem.DoesNotExist):
            return Response(
                {"error": "Cart item not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        if quantity < 1:
            item.delete()
            return Response({"message": "Item removed from cart"})

        item.quantity = quantity
        item.save()

        return Response({"message": "Cart item updated"})


class RemoveCartItemView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, item_id):
        try:
            cart = request.user.cart
            item = cart.items.get(id=item_id)
        except (Cart.DoesNotExist, CartItem.DoesNotExist):
            return Response(
                {"error": "Cart item not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        item.delete()
        return Response({"message": "Item removed from cart"})