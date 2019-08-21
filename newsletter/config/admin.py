from django.contrib import admin
from .models import QueueFilter, ProcessedEmail


@admin.register(ProcessedEmail)
class ProcessedEmailAdmin(admin.ModelAdmin):
    list_display = ("owner", "subject", "email_id", "processed_on")


@admin.register(QueueFilter)
class QueueFilterAdmin(admin.ModelAdmin):
    list_display = ("queue_name", "label_id", "owner")
