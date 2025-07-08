from django.db import models
from django.contrib.auth.models import User


class UploadedImage(models.Model):
    image = models.ImageField(upload_to="emotions", null=True)
    uploaded_time = models.DateTimeField(auto_now_add=True)
    registered_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)


class AnalysisResult(models.Model):
    date_time = models.DateTimeField(auto_now_add=True)
    detected_image = models.ForeignKey(UploadedImage, on_delete=models.CASCADE, related_name='detect_emotions', null=True)




