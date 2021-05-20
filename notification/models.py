from django.db import models
from django.utils import timezone
from django.conf import settings
# Create your models here.

class Notification(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField(max_length=500)
    timestamp = models.DateTimeField(default=timezone.now)
    creator = models.ForeignKey(to = settings.AUTH_USER_MODEL, on_delete= models.CASCADE)

    def __str__(self):
        return self.title