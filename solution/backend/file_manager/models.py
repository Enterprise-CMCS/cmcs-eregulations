from django.db import models


class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploaded_files/')  # Use models.FileField from django.db.models.fields
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name
