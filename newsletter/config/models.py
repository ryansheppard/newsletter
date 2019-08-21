from django.db import models
from django.contrib.auth.models import User


class QueueFilter(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    queue_name = models.CharField(max_length=256, blank=False, null=False)
    label_id = models.CharField(max_length=256, blank=False, null=False)

    def __str__(self):
        return f"{self.owner} - {self.queue_name}"


class ProcessedEmail(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    email_id = models.CharField(max_length=256, blank=False, null=False)
    subject = models.CharField(max_length=256, blank=False, null=False)
    sent_to = models.ForeignKey(QueueFilter, on_delete=models.CASCADE)
    processed_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject}"
