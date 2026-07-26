from django.conf import settings
from django.db import models
 
from .pet import Pet
 
 
class AdoptionRequest(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    )
 
    pet = models.ForeignKey(
        Pet,
        on_delete=models.CASCADE,
        related_name='adoption_requests'
    )
    adopter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='adoption_requests'
    )
    message = models.TextField(help_text="Why do you want to adopt this pet?")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
 
    class Meta:
        ordering = ['-created_at']
        constraints = [
            # One request per adopter per pet — enforced by the database, so
            # concurrent submissions cannot slip through.
            models.UniqueConstraint(
                fields=['pet', 'adopter'],
                name='unique_adoption_request_per_pet_and_adopter',
            )
        ]
        indexes = [
            models.Index(fields=['status'], name='adoption_request_status_idx'),
        ]
 
    def __str__(self):
        return f"Request by {self.adopter.username} for {self.pet.name} - [{self.status}]"
 
    @property
    def is_pending(self):
        return self.status == 'Pending'