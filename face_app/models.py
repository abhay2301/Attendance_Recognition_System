from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator
import uuid


class Person(models.Model):
    """Model to store person information for face recognition."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = 'Person'
        verbose_name_plural = 'People'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class FaceImage(models.Model):
    """Model to store face images and their encodings."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='face_images')
    image = models.ImageField(
        upload_to='faces',
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])]
    )
    encoding = models.JSONField(blank=True, null=True, help_text='Face encoding data')
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Face Image'
        verbose_name_plural = 'Face Images'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.person.name} - {self.image.name}"


class RecognitionLog(models.Model):
    """Model to log face recognition attempts."""
    STATUS_CHOICES = [
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('NO_FACE', 'No Face Detected'),
        ('MULTIPLE_FACES', 'Multiple Faces Detected'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    person_id = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True, blank=True, related_name='recognition_logs')
    input_image = models.ImageField(upload_to='recognition_logs/%Y/%m/%d/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='FAILED')
    confidence = models.FloatField(blank=True, null=True, help_text='Recognition confidence score')
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Recognition Log'
        verbose_name_plural = 'Recognition Logs'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.status} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
