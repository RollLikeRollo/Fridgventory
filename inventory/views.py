from io import BytesIO
from typing import List

from django.db.models import QuerySet
from django.http import FileResponse, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext as _

from .models import Item, Location, Tag


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
            item, _ = Item.objects.get_or_create(name=name)
            item.desired_quantity = desired
            item.current_quantity = current
            item.save()

            locations: List[Location] = [Location.objects.get_or_create(name=n)[0] for n in location_names]
            tags: List[Tag] = [Tag.objects.get_or_create(name=n)[0] for n in tag_names]
            item.locations.set(locations)
            item.tags.set(tags)
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
        item.name = request.POST.get("name", item.name).strip() or item.name
        item.desired_quantity = int(request.POST.get("desired_quantity", item.desired_quantity) or 0)
        item.current_quantity = int(request.POST.get("current_quantity", item.current_quantity) or 0)
        location_names = [s.strip() for s in request.POST.get("locations", "").split(",") if s.strip()]
        tag_names = [s.strip() for s in request.POST.get("tags", "").split(",") if s.strip()]

        item.save()
        if location_names:
            locations = [Location.objects.get_or_create(name=n)[0] for n in location_names]
            item.locations.set(locations)
        if tag_names:
            tags = [Tag.objects.get_or_create(name=n)[0] for n in tag_names]
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
