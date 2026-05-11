from django.db import models
from django.contrib.auth.models import AbstractUser  # mM* - import form

# Create your models here.

# 1. User Model: 
class User(AbstractUser):
    ROLE_CHOICES = [
        ("AD", "Admin"),
        ("IN", "Instructor"),
        ("ST", "Student"),
        ("SP", "Sponsor"),
    ]
    
    GENDER_CHOICES = [
        ("M", "Male"),
        ("F", "Female"),
        ("O", "Other"),
    ]
    
    role = models.CharField(max_length=2, choices = ROLE_CHOICES, default = "ST")
    phone_no = models.CharField(max_length = 20, unique = True, blank = True, null = True)
    address = models.CharField(max_length=50, blank = True, null = True)
    photo = models.ImageField(upload_to = 'profile_pic/', blank = True, null = True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null = True)
    
    def __str__(self):
        return (f"{self.username} ({self.role})")
    