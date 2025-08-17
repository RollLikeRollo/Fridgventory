from io import BytesIO
import os
from typing import List
import json

from django.db.models import QuerySet
from django.http import FileResponse, HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST
import json
import requests
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q

from .models import Item, Location, Tag, UserSettings


def index(request: HttpRequest) -> HttpResponse:
    items: QuerySet[Item] = Item.objects.prefetch_related("locations", "tags").order_by("name")
    return render(request, "inventory/index.html", {"items": items})


def item_create(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        desired = int(request.POST.get("desired_quantity", 0) or 0)
        current = int(request.POST.get("current_quantity", 0) or 0)
        location_names = [s.strip() for s in request.POST.get("locations", "").split(",") if s.strip()]
        tag_names = [s.strip() for s in request.POST.get("tags", "").split(",") if s.strip()]

        if name:
            # Check for existing item
            existing_item = Item.objects.filter(name=name).first()
            if existing_item:
                return render(
                    request,
                    "inventory/item_form.html",
                    {
                        "locations": Location.objects.order_by("name").all(),
                        "tags": Tag.objects.order_by("name").all(),
                        "error": _("An item with this name already exists"),
                        "form_data": {
                            "name": name,
                            "desired_quantity": desired,
                            "current_quantity": current,
                            "locations": ", ".join(location_names),
                            "tags": ", ".join(tag_names),
                        }
                    },
                )
            
            item = Item.objects.create(
                name=name,
                desired_quantity=desired,
                current_quantity=current
            )

            # Create/get locations and tags, tracking new ones
            new_locations = []
            new_tags = []
            
            locations = []
            for name_loc in location_names:
                loc, created = Location.objects.get_or_create(name=name_loc)
                locations.append(loc)
                if created:
                    new_locations.append(name_loc)
            
            tags = []
            for name_tag in tag_names:
                tag, created = Tag.objects.get_or_create(name=name_tag)
                tags.append(tag)
                if created:
                    new_tags.append(name_tag)
            
            item.locations.set(locations)
            item.tags.set(tags)
            
            # Success message can be added to session if needed
            return redirect("inventory:index")

    locations_all = Location.objects.order_by("name").all()
    tags_all = Tag.objects.order_by("name").all()
    return render(
        request,
        "inventory/item_form.html",
        {"locations": locations_all, "tags": tags_all},
    )


def item_edit(request: HttpRequest, item_id: int) -> HttpResponse:
    item = get_object_or_404(Item, id=item_id)
    
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        desired = int(request.POST.get("desired_quantity", 0) or 0)
        current = int(request.POST.get("current_quantity", 0) or 0)
        location_names = [s.strip() for s in request.POST.get("locations", "").split(",") if s.strip()]
        tag_names = [s.strip() for s in request.POST.get("tags", "").split(",") if s.strip()]

        if not name:
            return render(
                request,
                "inventory/item_form.html",
                {
                    "item": item,
                    "locations": Location.objects.order_by("name").all(),
                    "tags": Tag.objects.order_by("name").all(),
                    "error": _("Item name is required"),
                    "form_data": {
                        "name": name,
                        "desired_quantity": desired,
                        "current_quantity": current,
                        "locations": ", ".join(location_names),
                        "tags": ", ".join(tag_names),
                    }
                },
            )
        
        # Check for duplicate names (excluding current item)
        existing_item = Item.objects.filter(name=name).exclude(id=item.id).first()
        if existing_item:
            return render(
                request,
                "inventory/item_form.html",
                {
                    "item": item,
                    "locations": Location.objects.order_by("name").all(),
                    "tags": Tag.objects.order_by("name").all(),
                    "error": _("An item with this name already exists"),
                    "form_data": {
                        "name": name,
                        "desired_quantity": desired,
                        "current_quantity": current,
                        "locations": ", ".join(location_names),
                        "tags": ", ".join(tag_names),
                    }
                },
            )

        # Update item
        item.name = name
        item.desired_quantity = desired
        item.current_quantity = current
        item.save()

        # Create/get locations and tags, tracking new ones
        new_locations = []
        new_tags = []
        
        locations = []
        for name_loc in location_names:
            loc, created = Location.objects.get_or_create(name=name_loc)
            locations.append(loc)
            if created:
                new_locations.append(name_loc)
        
        tags = []
        for name_tag in tag_names:
            tag, created = Tag.objects.get_or_create(name=name_tag)
            tags.append(tag)
            if created:
                new_tags.append(name_tag)
        
        item.locations.set(locations)
        item.tags.set(tags)
        
        return redirect("inventory:index")

    locations_all = Location.objects.order_by("name").all()
    tags_all = Tag.objects.order_by("name").all()
    return render(
        request,
        "inventory/item_form.html",
        {"item": item, "locations": locations_all, "tags": tags_all},
    )


def item_delete(request: HttpRequest, item_id: int) -> HttpResponse:
    item = get_object_or_404(Item, id=item_id)
    if request.method == "POST":
        item.delete()
        return redirect("inventory:index")
    return render(request, "inventory/item_delete_confirm.html", {"item": item})


def generate_shopping_list_text(request: HttpRequest) -> HttpResponse:
    lines: List[str] = []
    for item in Item.objects.order_by("name"):
        missing = item.missing_quantity
        if missing > 0:
            lines.append(f"{item.name}: {missing}")
    content = "\n".join(lines) or _("All stocked!")
    response = HttpResponse(content, content_type="text/plain")
    response["Content-Disposition"] = 'attachment; filename="shopping_list.txt"'
    return response


def generate_shopping_list_image(request: HttpRequest) -> HttpResponse:
    from PIL import Image, ImageDraw, ImageFont

    items = [
        (item.name, item.missing_quantity)
        for item in Item.objects.order_by("name")
        if item.missing_quantity > 0
    ]

    if not items:
        items = [("All stocked!", 0)]

    width = 800
    line_height = 40
    height = 80 + line_height * len(items)
    image = Image.new("RGB", (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 24)
    except Exception:
        font = ImageFont.load_default()

    y = 20
    draw.text((20, y), _("Shopping List"), fill=(0, 0, 0), font=font)
    y += 40
    for name, missing in items:
        line = name if missing == 0 else f"{name}: {missing}"
        draw.text((20, y), line, fill=(0, 0, 0), font=font)
        y += line_height

    output = BytesIO()
    image.save(output, format="PNG")
    output.seek(0)
    return FileResponse(output, filename="shopping_list.png", content_type="image/png")


def settings(request: HttpRequest) -> HttpResponse:
    """Settings page with tag and location management."""
    tags = Tag.objects.order_by("name").all()
    locations = Location.objects.order_by("name").all()
    user_settings = UserSettings.get_settings()
    return render(request, "inventory/settings.html", {
        "tags": tags, 
        "locations": locations,
        "user_settings": user_settings
    })


def tag_create(request: HttpRequest) -> HttpResponse:
    """Create a new tag."""
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        if name:
            Tag.objects.get_or_create(name=name)
        return redirect("inventory:settings")
    return redirect("inventory:settings")


def tag_edit(request: HttpRequest, tag_id: int) -> HttpResponse:
    """Edit an existing tag."""
    tag = get_object_or_404(Tag, id=tag_id)
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        color = request.POST.get("color", "").strip()
        emoji = request.POST.get("emoji", "").strip()
        
        # Update name if provided and different
        if name and name != tag.name:
            tag.name = name
        
        # Update color if provided and valid
        if color and color.startswith('#') and len(color) == 7:
            tag.color = color
        
        # Update emoji if provided
        if emoji:
            tag.emoji = emoji
        
        tag.save()
        return redirect("inventory:settings")
    return render(request, "inventory/tag_edit.html", {"tag": tag})


def tag_delete(request: HttpRequest, tag_id: int) -> HttpResponse:
    """Delete a tag."""
    tag = get_object_or_404(Tag, id=tag_id)
    if request.method == "POST":
        tag.delete()
        return redirect("inventory:settings")
    return render(request, "inventory/tag_delete_confirm.html", {"tag": tag})


def location_create(request: HttpRequest) -> HttpResponse:
    """Create a new location."""
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        if name:
            Location.objects.get_or_create(name=name)
        return redirect("inventory:settings")
    return redirect("inventory:settings")


def location_edit(request: HttpRequest, location_id: int) -> HttpResponse:
    """Edit an existing location."""
    location = get_object_or_404(Location, id=location_id)
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        color = request.POST.get("color", "").strip()
        emoji = request.POST.get("emoji", "").strip()
        
        # Update name if provided and different
        if name and name != location.name:
            location.name = name
        
        # Update color if provided and valid
        if color and color.startswith('#') and len(color) == 7:
            location.color = color
        
        # Update emoji if provided
        if emoji:
            location.emoji = emoji
        
        location.save()
        return redirect("inventory:settings")
    return render(request, "inventory/location_edit.html", {"location": location})


def location_delete(request: HttpRequest, location_id: int) -> HttpResponse:
    """Delete a location."""
    location = get_object_or_404(Location, id=location_id)
    if request.method == "POST":
        location.delete()
        return redirect("inventory:settings")
    return render(request, "inventory/location_delete_confirm.html", {"location": location})


def update_defaults(request: HttpRequest) -> HttpResponse:
    """Update default colors and emojis for tags and locations."""
    if request.method == "POST":
        settings = UserSettings.get_settings()
        
        # Update tag defaults
        tag_color = request.POST.get("default_tag_color", "").strip()
        tag_emoji = request.POST.get("default_tag_emoji", "").strip()
        
        if tag_color and tag_color.startswith('#') and len(tag_color) == 7:
            settings.default_tag_color = tag_color
        
        if tag_emoji:
            settings.default_tag_emoji = tag_emoji
        
        # Update location defaults
        location_color = request.POST.get("default_location_color", "").strip()
        location_emoji = request.POST.get("default_location_emoji", "").strip()
        
        if location_color and location_color.startswith('#') and len(location_color) == 7:
            settings.default_location_color = location_color
        
        if location_emoji:
            settings.default_location_emoji = location_emoji
        
        settings.save()
        
    return redirect("inventory:settings")


@require_POST
def item_update_field(request: HttpRequest, item_id: int) -> JsonResponse:
    """Update a single field of an item via AJAX."""
    try:
        item = get_object_or_404(Item, id=item_id)
        field = request.POST.get('field', '').strip()
        value = request.POST.get('value', '').strip()
        
        # Validate field name
        allowed_fields = ['name', 'desired_quantity', 'current_quantity']
        if field not in allowed_fields:
            return JsonResponse({
                'success': False,
                'error': _('Invalid field name')
            })
        
        # Validate and convert value
        if field == 'name':
            if not value:
                return JsonResponse({
                    'success': False,
                    'error': _('Name cannot be empty')
                })
            
            # Check for duplicate names
            if Item.objects.filter(name=value).exclude(id=item.id).exists():
                return JsonResponse({
                    'success': False,
                    'error': _('An item with this name already exists')
                })
            
            item.name = value
            
        elif field in ['desired_quantity', 'current_quantity']:
            try:
                numeric_value = int(value)
                if numeric_value < 0:
                    return JsonResponse({
                        'success': False,
                        'error': _('Quantity cannot be negative')
                    })
                setattr(item, field, numeric_value)
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'error': _('Please enter a valid number')
                })
        
        # Save the item
        item.save()
        
        return JsonResponse({
            'success': True,
            'message': _('Item updated successfully'),
            'missing_quantity': item.missing_quantity  # Include updated missing quantity
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': _('An error occurred while updating the item')
        })


def autocomplete_tags(request: HttpRequest) -> JsonResponse:
    """API endpoint for tag autocomplete."""
    query = request.GET.get('q', '').strip()
    if not query:
        return JsonResponse({'results': []})
    
    # Search for existing tags that match the query
    tags = Tag.objects.filter(
        name__icontains=query
    ).order_by('name')[:10]  # Limit to 10 results
    
    results = []
    for tag in tags:
        results.append({
            'id': tag.id,
            'name': tag.name,
            'emoji': tag.emoji,
            'color': tag.color,
            'type': 'existing'
        })
    
    return JsonResponse({'results': results})


def autocomplete_locations(request: HttpRequest) -> JsonResponse:
    """API endpoint for location autocomplete."""
    query = request.GET.get('q', '').strip()
    if not query:
        return JsonResponse({'results': []})
    
    # Search for existing locations that match the query
    locations = Location.objects.filter(
        name__icontains=query
    ).order_by('name')[:10]  # Limit to 10 results
    
    results = []
    for location in locations:
        results.append({
            'id': location.id,
            'name': location.name,
            'emoji': location.emoji,
            'color': location.color,
            'type': 'existing'
        })
    
    return JsonResponse({'results': results})


