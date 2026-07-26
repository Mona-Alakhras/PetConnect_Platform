"""Forms and upload validation for the petcare app."""
 
from django import forms
from django.core.exceptions import ValidationError
from django.template.defaultfilters import filesizeformat
 
from .models import Pet
 
# Upload guard rails for pet photos.
MAX_IMAGES_PER_PET = 3
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB
ALLOWED_IMAGE_TYPES = {
    'image/jpeg',
    'image/png',
    'image/webp',
    'image/gif',
}
 
 
class PetForm(forms.ModelForm):
    """Validates a pet listing.
 
    The dashboard renders its own markup, so this form is used purely for
    server-side validation and cleaning rather than for rendering widgets.
    """
 
    class Meta:
        model = Pet
        fields = ['name', 'species', 'breed', 'age', 'location', 'status']
 
    def clean_name(self):
        name = self.cleaned_data['name'].strip()
        if len(name) < 2:
            raise ValidationError("Pet name must be at least 2 characters long.")
        return name
 
    def clean_breed(self):
        return self.cleaned_data['breed'].strip()
 
    def clean_age(self):
        return self.cleaned_data['age'].strip()
 
    def clean_location(self):
        location = self.cleaned_data['location'].strip()
        if len(location) < 2:
            raise ValidationError("Please enter a valid location.")
        return location
 
 
def validate_pet_images(files, existing_count=0):
    """Check a list of uploaded files before any of them is saved.
 
    Returns the list of accepted files, or raises ``ValidationError`` with a
    message suitable for showing to the user.
    """
    if not files:
        return []
 
    remaining = MAX_IMAGES_PER_PET - existing_count
    if remaining <= 0:
        raise ValidationError(
            f"This pet already has the maximum of {MAX_IMAGES_PER_PET} images."
        )
 
    if len(files) > remaining:
        raise ValidationError(
            f"You can upload at most {MAX_IMAGES_PER_PET} images per pet "
            f"({remaining} slot{'s' if remaining != 1 else ''} left)."
        )
 
    for uploaded in files:
        if uploaded.size > MAX_IMAGE_SIZE:
            raise ValidationError(
                f'"{uploaded.name}" is {filesizeformat(uploaded.size)}. '
                f"Each image must be under {filesizeformat(MAX_IMAGE_SIZE)}."
            )
 
        content_type = (uploaded.content_type or '').lower()
        if content_type not in ALLOWED_IMAGE_TYPES:
            raise ValidationError(
                f'"{uploaded.name}" is not a supported image. '
                "Please upload a JPG, PNG, WEBP or GIF file."
            )
 
    return list(files)
 
 