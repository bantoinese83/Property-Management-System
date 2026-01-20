from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from properties.models import Property

from .models import Document

User = get_user_model()


class DocumentTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpassword", first_name="Test", last_name="User"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.property = Property.objects.create(property_name="Test Property", address="123 Test St", owner=self.user)

        self.test_file = SimpleUploadedFile("test_doc.txt", b"test content", content_type="text/plain")

    def test_upload_document_with_model_name(self):
        url = "/api/documents/"
        data = {
            "title": "Property Document",
            "description": "A test document for property",
            "model_name": "property",
            "object_id": self.property.id,
            "file": self.test_file,
        }

        response = self.client.post(url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        doc = Document.objects.get(id=response.data["id"])
        self.assertEqual(doc.title, "Property Document")
        self.assertEqual(doc.content_object, self.property)
        self.assertEqual(doc.uploaded_by, self.user)
        # Use in instead of endswith to be safer with storage backends
        self.assertIn("test_doc", doc.file.name)

    def test_list_documents_by_model_name(self):
        # Create a document first
        Document.objects.create(
            title="Existing Doc",
            file=self.test_file,
            content_type=ContentType.objects.get_for_model(Property),
            object_id=self.property.id,
            uploaded_by=self.user,
        )

        url = "/api/documents/"
        response = self.client.get(url, {"model_name": "property", "object_id": self.property.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "Existing Doc")

    def test_upload_invalid_model_name(self):
        url = "/api/documents/"
        data = {"title": "Invalid Document", "model_name": "non_existent_model", "object_id": 1, "file": self.test_file}

        response = self.client.post(url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("model_name", response.data)
