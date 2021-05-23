from django.db import models
from django.utils import timezone
from django.conf import settings
from fcm_django.models import FCMDevice
# Create your models here.


class Notification(models.Model):

    title = models.CharField(max_length=100,unique=False)
    content = models.TextField(max_length=500,unique=False,blank=True)
    created_on = models.DateTimeField(default=timezone.now)
    receivers = models.ManyToManyField(to= settings.AUTH_USER_MODEL, related_name = 'received_notifications')
    sender = models.ForeignKey(to = settings.AUTH_USER_MODEL, on_delete= models.CASCADE ,related_name = 'sent_notifications')

    def __str__(self):
        return self.title

class NotificationStatus(models.Model):

    notification = models.ForeignKey(to = Notification,on_delete=models.CASCADE )
    recipient = models.ForeignKey( to = settings.AUTH_USER_MODEL, on_delete = models.CASCADE,related_name = 'notification_status')
    is_read = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Notification Status"

    def __str__(self):
        return f"Notification#{self.notification.id}-{self.recipient.username}"
