from django.contrib import admin

from .models import Item, Tag, Location


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("name", "desired_quantity", "current_quantity")
    search_fields = ("name",)
    filter_horizontal = ("locations", "tags")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    search_fields = ("name",)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    search_fields = ("name",)
