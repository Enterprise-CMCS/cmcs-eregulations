
from django.db import models
import os

class UploadedFile(models.Model):
    name = models.CharField(max_length=512, null=True, blank=True)
    file = models.FileField(upload_to='uploaded_files/')
    
    def filename(self):
        return os.path.basename(self.file.name)
