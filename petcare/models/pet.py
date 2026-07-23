from io import BytesIO
from django.conf import settings
from django.core.files.base import ContentFile
from django.db import models
from PIL import Image


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

    age = models.CharField(max_length=50)

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


    def __str__(self):
        return f'{self.name} ({self.species})'


class PetImage(models.Model):
  pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='images')
  image = models.ImageField(upload_to='pet_images/')

  def save(self, *args, **kwargs):
    if self.image:
      # فتح الصورة باستخدام مكتبة Pillow
      img = Image.open(self.image)

      # تحويل الألوان إلى RGB إذا كانت بصيغة RGBA أو شفافة لتجنب أخطاء الحفظ
      if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')

      # حفظ الصورة في الذاكرة المؤقتة بصيغة WEBP وبجودة ممتازة (85)
      buffer = BytesIO()
      img.save(buffer, format='WEBP', quality=85)
      buffer.seek(0)

      # استبدال امتداد الملف الحالي إلى .webp
      file_name = self.image.name.rsplit('.', 1)[0] + '.webp'
      self.image.save(file_name, ContentFile(buffer.read()), save=False)

    super().save(*args, **kwargs)

  def __str__(self):
    return f'{self.pet.name} Image'