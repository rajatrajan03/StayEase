from django.db import models
from django.contrib.auth.models import User
from properties.models import Room


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]

    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="bookings")
    tenant = models.ForeignKey(User, on_delete=models.CASCADE)

    move_in_date = models.DateField()

    rent_amount = models.PositiveIntegerField()
    security_amount = models.PositiveIntegerField()
    total_amount = models.PositiveIntegerField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):

        # Auto calculate amounts
        self.rent_amount = self.room.rent
        self.security_amount = self.room.rent
        self.total_amount = self.rent_amount + self.security_amount

        super().save(*args, **kwargs)

        # Capacity Logic 
        confirmed_count = Booking.objects.filter(
            room=self.room,
            status="confirmed"
        ).count()

        if confirmed_count >= self.room.capacity:
            self.room.is_available = False
        else:
            self.room.is_available = True

        self.room.save()

    def __str__(self):
        return f"{self.tenant.username} - Room {self.room.room_number}"