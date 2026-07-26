from io import BytesIO
 
from django.conf import settings
from django.core.files.base import ContentFile
from django.db import models
from django.urls import reverse
from PIL import Image
 
# Uploaded images are re-encoded to WebP at this quality.
WEBP_QUALITY = 85
 
# Longest edge, in pixels, kept after resizing. Anything larger is scaled down.
MAX_IMAGE_EDGE = 1600
 
 
class Pet(models.Model):
 
    SPECIES_CHOICES = [
        ('Dog', 'Dogs'),
        ('Cat', 'Cats'),
        ('Bird', 'Birds'),
        ('Other', 'Others'),
    ]
 
    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Adopted', 'Adopted'),
    ]
 
    name = models.CharField(max_length=100)
 
    species = models.CharField(
        max_length=50,
        choices=SPECIES_CHOICES
    )
 
    breed = models.CharField(max_length=100)
 
    age = models.CharField(
        max_length=50,
        help_text="Free text, e.g. '2 years' or '6 months'."
    )
 
    location = models.CharField(max_length=100)
 
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Available'
    )
 
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='pets'
    )
 
    created_at = models.DateTimeField(
        auto_now_add=True
    )
 
    class Meta:
        ordering = ['-created_at', '-id']
        indexes = [
            models.Index(fields=['status', 'species'], name='pet_status_species_idx'),
            models.Index(fields=['owner'], name='pet_owner_idx'),
        ]
 
    def __str__(self):
        return f'{self.name} ({self.species})'
 
    def get_absolute_url(self):
        return reverse('pet_detail', args=[self.pk])
 
    @property
    def is_available(self):
        return self.status == 'Available'
 
    @property
    def primary_image(self):
        """First uploaded image, or None. Safe to use with prefetched images."""
        images = self.images.all()
        return images[0] if images else None
 
 
class PetImage(models.Model):
    pet = models.ForeignKey(
        Pet,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='pet_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
 
    class Meta:
        ordering = ['id']
 
    def save(self, *args, **kwargs):
        # Re-encode freshly uploaded files to WebP. Already-stored images keep
        # their file untouched so re-saving a row does not recompress it.
        if self.image and not self.image.name.lower().endswith('.webp'):
            img = Image.open(self.image)
 
            # Flatten transparency and exotic modes down to RGB.
            if img.mode in ('RGBA', 'P', 'LA'):
                img = img.convert('RGB')
 
            img.thumbnail((MAX_IMAGE_EDGE, MAX_IMAGE_EDGE), Image.LANCZOS)
 
            buffer = BytesIO()
            img.save(buffer, format='WEBP', quality=WEBP_QUALITY)
            buffer.seek(0)
 
            file_name = self.image.name.rsplit('.', 1)[0] + '.webp'
            self.image.save(file_name, ContentFile(buffer.read()), save=False)
 
        super().save(*args, **kwargs)
 
    def __str__(self):
        return f'{self.pet.name} Image'
 