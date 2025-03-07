from django.contrib import admin

# Register your models here.
from .models import *


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Property._meta.fields]

@admin.register(BuyerRequest)
class BuyerRequestAdmin(admin.ModelAdmin):
    list_display = [field.name for field in BuyerRequest._meta.fields]

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Wishlist._meta.fields]

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = [field.name for field in CustomUser._meta.fields]
    
@admin.register(PropertyMedia)
class PropertyMediaAdmin(admin.ModelAdmin):
    list_display = [field.name for field in PropertyMedia._meta.fields]
    
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Notification._meta.fields]
    
