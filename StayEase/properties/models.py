from django.db import models
from django.contrib.auth.models import User

class Property(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="properties")
    # Basic Info
    name = models.CharField(max_length=200)
    description = models.TextField()
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)
    landmark = models.CharField(max_length=150, blank=True, null=True)
    main_image = models.ImageField(upload_to="properties/", blank=True, null=True)
    back_image = models.ImageField(upload_to="properties/", blank=True, null=True)
    
    # Business Control
    is_active = models.BooleanField(default=False)
    is_paid_listing = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class Room(models.Model):

    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name="rooms"
    )

    room_number = models.CharField(max_length=20)
    rent = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.IntegerField()
    is_available = models.BooleanField(default=True)
    image = models.ImageField(upload_to="rooms/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.property.name} - Room {self.room_number}"
    
