import re
from django.db import models
from django.core.cache import cache


def get_tag_color_and_emoji(name: str) -> tuple[str, str]:
    """Automatically assign color and emoji based on tag name."""
    name_lower = name.lower().strip()
    
    # Define color and emoji mappings
    mappings = {
        # Food categories
        r'(vegetables?|veggie|green|lettuce|spinach|broccoli|cabbage)': ('#22c55e', '🥬'),
        r'(fruits?|apple|banana|orange|berry|grape|citrus)': ('#f59e0b', '🍎'),
        r'(meat|beef|chicken|pork|protein|bacon|ham)': ('#dc2626', '🥩'),
        r'(dairy|milk|cheese|yogurt|butter|cream)': ('#3b82f6', '🥛'),
        r'(grain|bread|rice|pasta|cereal|wheat)': ('#a16207', '🌾'),
        r'(beverage|drink|juice|soda|coffee|tea|water)': ('#06b6d4', '🧃'),
        r'(snack|chip|cookie|candy|chocolate)': ('#f97316', '🍿'),
        r'(frozen|ice|cold)': ('#0ea5e9', '❄️'),
        r'(spice|seasoning|salt|pepper|herb)': ('#7c2d12', '🧂'),
        r'(condiment|sauce|ketchup|mustard|mayo)': ('#eab308', '🍯'),
        r'(baking|flour|sugar|vanilla)': ('#e879f9', '🧁'),
        r'(canned|jarred|preserved)': ('#6b7280', '🥫'),
        r'(organic|natural|healthy)': ('#16a34a', '🌱'),
        r'(vegan|plant)': ('#15803d', '🌿'),
        r'(gluten.?free|gf)': ('#a855f7', '🌾'),
        r'(vitamin|supplement|health)': ('#059669', '💊'),
        r'(breakfast|morning)': ('#fbbf24', '🌅'),
        r'(lunch|noon)': ('#fb923c', '🌞'),
        r'(dinner|evening)': ('#7c3aed', '🌙'),
        r'(dessert|sweet)': ('#ec4899', '🍰'),
        r'(bulk|large|big)': ('#374151', '📦'),
        r'(fresh|new)': ('#10b981', '✨'),
        r'(dried|dry)': ('#92400e', '🏜️'),
        r'(low.?fat|diet)': ('#84cc16', '⚖️'),
        r'(high.?protein|protein)': ('#dc2626', '💪'),
    }
    
    # Check each pattern
    for pattern, (color, emoji) in mappings.items():
        if re.search(pattern, name_lower):
            return color, emoji
    
    # Default fallback - will be overridden by UserSettings in the model save method
    return '#6b7280', '🏷️'


def get_location_color_and_emoji(name: str) -> tuple[str, str]:
    """Automatically assign color and emoji based on location name."""
    name_lower = name.lower().strip()
    
    # Define color and emoji mappings for locations
    mappings = {
        r'(fridge|refrigerat)': ('#3b82f6', '🧊'),
        r'(freezer|frozen)': ('#0ea5e9', '❄️'),
        r'(pantry|cabinet|cupboard)': ('#a16207', '🏠'),
        r'(counter|kitchen)': ('#6b7280', '🏠'),
        r'(basement|cellar|storage)': ('#374151', '🏚️'),
        r'(garage)': ('#525252', '🏠'),
        r'(wine|alcohol)': ('#7c2d12', '🍷'),
        r'(spice|seasoning)': ('#ea580c', '🧂'),
        r'(bread|bakery)': ('#d97706', '🍞'),
        r'(fruit|produce)': ('#f59e0b', '🍎'),
        r'(vegetable|veggie)': ('#22c55e', '🥬'),
        r'(meat|protein)': ('#dc2626', '🥩'),
        r'(cheese|dairy)': ('#3b82f6', '🧀'),
        r'(door|shelf)': ('#6b7280', '🚪'),
        r'(drawer)': ('#8b5cf6', '📦'),
    }
    
    # Check each pattern
    for pattern, (color, emoji) in mappings.items():
        if re.search(pattern, name_lower):
            return color, emoji
    
    # Default fallback - will be overridden by UserSettings in the model save method
    return '#6b7280', '📍'


class UserSettings(models.Model):
    """Model to store user-configurable default settings for colors and emojis."""
    # Singleton pattern - only one settings record should exist
    id = models.AutoField(primary_key=True)
    
    # Default colors and emojis for tags
    default_tag_color = models.CharField(max_length=7, default='#6b7280', help_text='Default color for new tags (hex format)')
    default_tag_emoji = models.CharField(max_length=10, default='🏷️', help_text='Default emoji for new tags')
    
    # Default colors and emojis for locations
    default_location_color = models.CharField(max_length=7, default='#6b7280', help_text='Default color for new locations (hex format)')
    default_location_emoji = models.CharField(max_length=10, default='📍', help_text='Default emoji for new locations')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "User Settings"
        verbose_name_plural = "User Settings"
    
    def save(self, *args, **kwargs):
        # Ensure only one settings record exists (singleton pattern)
        if not self.pk and UserSettings.objects.exists():
            # If trying to create a new record when one already exists, update the existing one
            existing = UserSettings.objects.first()
            existing.default_tag_color = self.default_tag_color
            existing.default_tag_emoji = self.default_tag_emoji
            existing.default_location_color = self.default_location_color
            existing.default_location_emoji = self.default_location_emoji
            existing.save()
            self.pk = existing.pk
        else:
            super().save(*args, **kwargs)
        
        # Clear cache when settings are updated
        cache.delete('user_settings')
    
    @classmethod
    def get_settings(cls):
        """Get the user settings, creating default ones if they don't exist."""
        settings = cache.get('user_settings')
        if settings is None:
            settings, _ = cls.objects.get_or_create(defaults={
                'default_tag_color': '#6b7280',
                'default_tag_emoji': '🏷️',
                'default_location_color': '#6b7280',
                'default_location_emoji': '📍',
            })
            cache.set('user_settings', settings, 300)  # Cache for 5 minutes
        return settings
    
    def __str__(self):
        return "User Settings"


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    color = models.CharField(max_length=7, default='#6b7280')  # Hex color
    emoji = models.CharField(max_length=10, default='🏷️')

    def save(self, *args, **kwargs):
        # Auto-assign color and emoji if not already set or if they are still default values
        settings = UserSettings.get_settings()
        default_color = settings.default_tag_color
        default_emoji = settings.default_tag_emoji
        
        if not self.color or self.color == default_color:
            pattern_color, pattern_emoji = get_tag_color_and_emoji(self.name)
            # Use pattern-based assignment if found, otherwise use user's default
            if pattern_color != '#6b7280':  # Pattern was found
                self.color, self.emoji = pattern_color, pattern_emoji
            else:  # No pattern found, use user's defaults
                self.color, self.emoji = default_color, default_emoji
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class Location(models.Model):
    name = models.CharField(max_length=100, unique=True)
    color = models.CharField(max_length=7, default='#6b7280')  # Hex color
    emoji = models.CharField(max_length=10, default='📍')

    def save(self, *args, **kwargs):
        # Auto-assign color and emoji if not already set or if they are still default values
        settings = UserSettings.get_settings()
        default_color = settings.default_location_color
        default_emoji = settings.default_location_emoji
        
        if not self.color or self.color == default_color:
            pattern_color, pattern_emoji = get_location_color_and_emoji(self.name)
            # Use pattern-based assignment if found, otherwise use user's default
            if pattern_color != '#6b7280':  # Pattern was found
                self.color, self.emoji = pattern_color, pattern_emoji
            else:  # No pattern found, use user's defaults
                self.color, self.emoji = default_color, default_emoji
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class Item(models.Model):
    name = models.CharField(max_length=200, unique=True)
    desired_quantity = models.PositiveIntegerField(default=0)
    current_quantity = models.PositiveIntegerField(default=0)
    locations = models.ManyToManyField(Location, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)

    @property
    def missing_quantity(self) -> int:
        missing = int(self.desired_quantity) - int(self.current_quantity)
        return missing if missing > 0 else 0

    def __str__(self) -> str:
        return self.name
