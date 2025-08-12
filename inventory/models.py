from django.db import models


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self) -> str:
        return self.name


class Location(models.Model):
    name = models.CharField(max_length=100, unique=True)

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
