from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

User = get_user_model()


class Document(models.Model):
    """File documents uploaded for various models"""

    FILE_TYPES = (
        ('pdf', 'PDF'),
        ('doc', 'Word Document'),
        ('docx', 'Word Document'),
        ('xls', 'Excel Spreadsheet'),
        ('xlsx', 'Excel Spreadsheet'),
        ('txt', 'Text File'),
        ('jpg', 'JPEG Image'),
        ('png', 'PNG Image'),
        ('gif', 'GIF Image'),
        ('other', 'Other'),
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # File storage
    file = models.FileField(upload_to='documents/')
    file_type = models.CharField(max_length=10, choices=FILE_TYPES)
    file_size = models.PositiveIntegerField(null=True, blank=True)

    # Generic relation to any model
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    # Audit
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='uploaded_documents')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['uploaded_by']),
        ]

    def __str__(self):
        return f"{self.title} ({self.file_type})"

    def get_file_type_display(self):
        return dict(self.FILE_TYPES).get(self.file_type, self.file_type)

    @property
    def file_url(self):
        """Get the file URL"""
        return self.file.url if self.file else None

    @property
    def file_name(self):
        """Get the file name from the path"""
        return self.file.name.split('/')[-1] if self.file else None