from django.urls import path

from . import views
from .ai import ai

app_name = "inventory"

urlpatterns = [
    path("", views.index, name="index"),
    path("items/new/", views.item_create, name="item_create"),
    path("items/<int:item_id>/edit/", views.item_edit, name="item_edit"),
    path("items/<int:item_id>/delete/", views.item_delete, name="item_delete"),
    path("items/<int:item_id>/update-field/", views.item_update_field, name="item_update_field"),
    path("shopping-list.txt", views.generate_shopping_list_text, name="shopping_list_text"),
    path("shopping-list.png", views.generate_shopping_list_image, name="shopping_list_image"),
    path("settings/", views.settings, name="settings"),
    path("settings/defaults/", views.update_defaults, name="update_defaults"),
    path("tags/new/", views.tag_create, name="tag_create"),
    path("tags/<int:tag_id>/edit/", views.tag_edit, name="tag_edit"),
    path("tags/<int:tag_id>/delete/", views.tag_delete, name="tag_delete"),
    path("locations/new/", views.location_create, name="location_create"),
    path("locations/<int:location_id>/edit/", views.location_edit, name="location_edit"),
    path("locations/<int:location_id>/delete/", views.location_delete, name="location_delete"),
    
    # API endpoints
    path("api/autocomplete/tags/", views.autocomplete_tags, name="autocomplete_tags"),
    path("api/autocomplete/locations/", views.autocomplete_locations, name="autocomplete_locations"),
    
    # AI
    path("ai/get-consumed-suggestions/", ai.get_consumed_suggestions, name="get_consumed_suggestions"),
]


