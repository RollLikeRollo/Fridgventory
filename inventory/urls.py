from django.urls import path

from . import views

app_name = "inventory"

urlpatterns = [
    path("", views.index, name="index"),
    path("items/new/", views.item_create, name="item_create"),
    path("items/<int:item_id>/edit/", views.item_edit, name="item_edit"),
    path("items/<int:item_id>/delete/", views.item_delete, name="item_delete"),
    path("shopping-list.txt", views.generate_shopping_list_text, name="shopping_list_text"),
    path("shopping-list.png", views.generate_shopping_list_image, name="shopping_list_image"),
]


