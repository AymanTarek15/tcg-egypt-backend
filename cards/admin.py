from django.contrib import admin
from .models import CardCategory, CardListing,YugiohCard,YugiohCardImage

admin.site.register(CardCategory)
admin.site.register(CardListing)
admin.site.register(YugiohCard)
admin.site.register(YugiohCardImage)