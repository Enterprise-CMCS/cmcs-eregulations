from django.shortcuts import render
from .models import UploadedFile


def file_manager(request):
    uploaded_files = UploadedFile.objects.all()
    return render(request, 'file_manager.html', {'uploaded_files': uploaded_files})
