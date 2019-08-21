from celery import shared_task
from .gmail_api import get_emails, sort_emails, add_email_to_queue
from .models import QueueFilter


@shared_task(bind=True)
def get_email_task(self):
    sorted_emails = []
    existing_filters = QueueFilter.objects.all()
    for existing_filter in existing_filters:
        filtered_emails = get_emails(existing_filter.owner, [existing_filter.label_id])
        sorted_emails.extend(sort_emails(existing_filter, filtered_emails))
    for email in sorted_emails:
        add_email_to_queue(email)

    return True
