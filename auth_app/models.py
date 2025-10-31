from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError

def validate_cin(value):
    if len(value) != 8:
        raise ValidationError("CIN must have exactly 8 characters")

def validate_phone(value):
    if len(value) != 8 or not value.isdigit():
        raise ValidationError("Phone number must have exactly 8 digits")

class User(AbstractUser):
    CIN = models.CharField(max_length=8, unique=True, validators=[validate_cin])
    phone = models.CharField(max_length=8, unique=True, validators=[validate_phone])
    # image = models.ImageField(upload_to='users/')
    image = models.ImageField(upload_to='users/', blank=True, null=True)  # Make optional
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)

    USERNAME_FIELD = "username"
    # REQUIRED_FIELDS = ["email", "CIN", "first_name", "last_name", "phone", "image"]
    REQUIRED_FIELDS = ["email", "CIN", "first_name", "last_name", "phone"]

    def __str__(self):
        return f"{self.username} ({self.CIN})"

    def to_json(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "CIN": self.CIN,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone": self.phone,
            "image": self.image.url if self.image else None
        }
