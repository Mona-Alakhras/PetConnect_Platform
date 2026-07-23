from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from .pet import Pet
class AdoptionRequest(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    )

    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='adoption_requests')
    adopter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)    
    message = models.TextField(help_text="Why do you want to adopt this pet?")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request by {self.adopter.username} for {self.pet.name} - [{self.status}]"


