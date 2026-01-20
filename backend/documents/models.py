from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
import os

class Document(models.Model):
    """
    General purpose document storage model.
    Can be attached to any other model (Property, Tenant, Lease, etc.)
    """
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to="documents/%Y/%m/%d/")
    file_type = models.CharField(max_length=100, blank=True)
    file_size = models.PositiveIntegerField(help_text="File size in bytes", null=True, blank=True)
    
    # Generic relation to attach to any model
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="uploaded_documents"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
            models.Index(fields=["title"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.file and not self.file_size:
            self.file_size = self.file.size
        
        if self.file and not self.file_type:
            _, extension = os.path.splitext(self.file.name)
            self.file_type = extension.lower().replace(".", "")
            
        super().save(*args, **kwargs)
