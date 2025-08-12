from inventory.models import Location


def on_ready() -> None:
    # Seed a few example locations if they do not exist
    for name in ["Fridge", "Freezer", "Pantry", "Cupboard", "Garage"]:
        Location.objects.get_or_create(name=name)


