from django.core.management.base import BaseCommand
from inventory.models import Tag, Location


class Command(BaseCommand):
    help = 'Update existing tags and locations with colors and emojis'

    def handle(self, *args, **options):
        # Update all existing tags
        tag_count = 0
        for tag in Tag.objects.all():
            # Force re-assignment by resetting color
            tag.color = '#6b7280'
            tag.save()  # This will trigger the auto-assignment
            tag_count += 1
            self.stdout.write(f'Updated tag: {tag.name} -> {tag.emoji} {tag.color}')

        # Update all existing locations
        location_count = 0
        for location in Location.objects.all():
            # Force re-assignment by resetting color
            location.color = '#6b7280'
            location.save()  # This will trigger the auto-assignment
            location_count += 1
            self.stdout.write(f'Updated location: {location.name} -> {location.emoji} {location.color}')

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully updated {tag_count} tags and {location_count} locations!'
            )
        )
