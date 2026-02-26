from django import forms
from .models import Property, Room

class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = [
            "name",
            "description",
            "address",
            "city",
            "state",
            "pincode",
            "landmark",
            "main_image",
            "back_image",
        ]

        widgets = {
            "name": forms.TextInput(attrs={"class": "form-input"}),
            "description": forms.Textarea(attrs={"class": "form-input", "rows": 4}),
            "address": forms.TextInput(attrs={"class": "form-input"}),
            "city": forms.TextInput(attrs={"class": "form-input"}),
            "state": forms.TextInput(attrs={"class": "form-input"}),
            "pincode": forms.TextInput(attrs={"class": "form-input"}),
            "landmark": forms.TextInput(attrs={"class": "form-input"}),
            "main_image": forms.FileInput(attrs={"class": "custom-file-input"}),
            "back_image": forms.FileInput(attrs={"class": "custom-file-input"}),
        }


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ["room_number", "rent", "capacity", "image", "is_available"]

        widgets = {
            "room_number": forms.TextInput(attrs={"class": "form-input"}),
            "rent": forms.NumberInput(attrs={
                "class": "form-input",
                "min": "500",
                "step": "500",
                }),
            "capacity": forms.NumberInput(attrs={"class": "form-input"}),
            "image": forms.FileInput(attrs={"class": "custom-file-input"}),
            "is_available": forms.CheckboxInput(attrs={"class": "form-checkbox"}),
        }
        
