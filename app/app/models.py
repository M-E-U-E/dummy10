from django.db import models

class Property(models.Model):
    city_name = models.CharField(max_length=255)
    property_name = models.CharField(max_length=255)
    hotel_id = models.CharField(max_length=50, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    rating = models.FloatField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    room_type = models.CharField(max_length=255, null=True, blank=True)
    image = models.URLField(null=True, blank=True)
    image_path = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return f"{self.property_name} in {self.city_name}"

class Summary(models.Model):
    property = models.OneToOneField(Property, on_delete=models.CASCADE, related_name='summary')
    description = models.TextField()

    def __str__(self):
        return f"Summary for {self.property.property_name}"
