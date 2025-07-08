from django.contrib import admin
from.models import UploadedImage, AnalysisResult 

# Register your models here.
admin.site.register(UploadedImage)
admin.site.register(AnalysisResult)