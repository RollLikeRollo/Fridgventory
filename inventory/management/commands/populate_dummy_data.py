import random
from django.core.management.base import BaseCommand
from django.db import models
from inventory.models import Item, Tag, Location


class Command(BaseCommand):
    help = 'Populate the database with dummy data for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--items',
            type=int,
            default=100,
            help='Number of items to create (default: 100)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before creating new data'
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            Item.objects.all().delete()
            Tag.objects.all().delete()
            Location.objects.all().delete()

        # Create locations
        location_names = [
            'Fridge', 'Freezer', 'Pantry', 'Cabinet', 'Counter', 'Basement Storage',
            'Garage Fridge', 'Wine Cellar', 'Spice Rack', 'Bread Box', 'Fruit Bowl',
            'Vegetable Drawer', 'Meat Drawer', 'Cheese Drawer', 'Door Shelves'
        ]
        
        locations = []
        for name in location_names:
            location, created = Location.objects.get_or_create(name=name)
            locations.append(location)
            if created:
                self.stdout.write(f'Created location: {name}')

        # Create tags
        tag_names = [
            'Dairy', 'Meat', 'Vegetables', 'Fruits', 'Grains', 'Beverages',
            'Snacks', 'Frozen', 'Organic', 'Gluten-Free', 'Vegan', 'Spices',
            'Condiments', 'Baking', 'Breakfast', 'Lunch', 'Dinner', 'Dessert',
            'Healthy', 'Quick Meal', 'Bulk', 'Imported', 'Local', 'Seasonal',
            'Low-Fat', 'High-Protein', 'Vitamins', 'Canned', 'Fresh', 'Dried'
        ]
        
        tags = []
        for name in tag_names:
            tag, created = Tag.objects.get_or_create(name=name)
            tags.append(tag)
            if created:
                self.stdout.write(f'Created tag: {name}')

        # Create items
        food_items = [
            # Dairy
            'Milk', 'Greek Yogurt', 'Cheddar Cheese', 'Mozzarella', 'Butter', 'Cream Cheese',
            'Sour Cream', 'Heavy Cream', 'Cottage Cheese', 'Parmesan Cheese', 'Feta Cheese',
            
            # Meat & Protein
            'Chicken Breast', 'Ground Beef', 'Salmon Fillet', 'Pork Chops', 'Turkey Slices',
            'Eggs', 'Bacon', 'Ham', 'Tuna Cans', 'Chicken Thighs', 'Shrimp', 'Ground Turkey',
            
            # Vegetables
            'Carrots', 'Broccoli', 'Spinach', 'Tomatoes', 'Potatoes', 'Onions', 'Bell Peppers',
            'Mushrooms', 'Lettuce', 'Cucumber', 'Zucchini', 'Garlic', 'Celery', 'Sweet Potatoes',
            'Green Beans', 'Corn', 'Peas', 'Cabbage', 'Cauliflower', 'Asparagus',
            
            # Fruits
            'Bananas', 'Apples', 'Oranges', 'Strawberries', 'Blueberries', 'Grapes', 'Lemons',
            'Limes', 'Avocados', 'Pineapple', 'Mango', 'Kiwi', 'Watermelon', 'Cantaloupe',
            'Peaches', 'Pears', 'Cherries', 'Raspberries', 'Blackberries',
            
            # Grains & Bread
            'White Bread', 'Whole Wheat Bread', 'Rice', 'Pasta', 'Quinoa', 'Oats', 'Cereal',
            'Crackers', 'Bagels', 'Tortillas', 'Brown Rice', 'Couscous', 'Barley',
            
            # Beverages
            'Orange Juice', 'Apple Juice', 'Coffee', 'Tea', 'Soda', 'Water Bottles',
            'Energy Drinks', 'Beer', 'Wine', 'Sparkling Water', 'Milk Alternative',
            
            # Pantry Items
            'Olive Oil', 'Salt', 'Black Pepper', 'Sugar', 'Flour', 'Baking Powder',
            'Vanilla Extract', 'Honey', 'Maple Syrup', 'Soy Sauce', 'Hot Sauce',
            'Ketchup', 'Mustard', 'Mayonnaise', 'Vinegar', 'Garlic Powder',
            
            # Snacks & Frozen
            'Chips', 'Cookies', 'Ice Cream', 'Frozen Pizza', 'Frozen Vegetables',
            'Nuts', 'Granola Bars', 'Popcorn', 'Chocolate', 'Candy', 'Crackers',
            
            # Additional items to reach 100+
            'Sandwich Meat', 'Pickles', 'Olives', 'Canned Beans', 'Soup Cans',
            'Instant Noodles', 'Peanut Butter', 'Jelly', 'Protein Bars', 'Yogurt Drinks'
        ]

        num_items = options['items']
        created_count = 0
        
        for i in range(num_items):
            # Select a random item name or create a numbered variant
            if i < len(food_items):
                item_name = food_items[i]
            else:
                base_name = random.choice(food_items)
                item_name = f"{base_name} #{i - len(food_items) + 2}"
            
            # Generate random quantities
            desired_qty = random.randint(1, 20)
            current_qty = random.randint(0, desired_qty + 5)
            
            # Create the item
            item, created = Item.objects.get_or_create(
                name=item_name,
                defaults={
                    'desired_quantity': desired_qty,
                    'current_quantity': current_qty
                }
            )
            
            if created:
                # Assign random locations (1-3 per item)
                item_locations = random.sample(locations, random.randint(1, 3))
                item.locations.set(item_locations)
                
                # Assign random tags (1-5 per item)
                item_tags = random.sample(tags, random.randint(1, 5))
                item.tags.set(item_tags)
                
                created_count += 1
                
                if created_count % 10 == 0:
                    self.stdout.write(f'Created {created_count} items...')

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created_count} items, '
                f'{len(locations)} locations, and {len(tags)} tags!'
            )
        )
        
        # Print some statistics
        total_items = Item.objects.count()
        missing_items = Item.objects.filter(current_quantity__lt=models.F('desired_quantity')).count()
        
        self.stdout.write(f'Total items in database: {total_items}')
        self.stdout.write(f'Items needing restocking: {missing_items}')
