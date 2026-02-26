from django.db import models
from django.contrib.auth.models import User
from properties.models import Property

class PropertyPayment(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)

    amount = models.IntegerField(default=1000)
    status = models.CharField(max_length=20, default="Success")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.property.name} - ₹{self.amount}"