import pika
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .gmail_api import get_labels
from .models import QueueFilter, ProcessedEmail


def index(request):
    return render(request, "config/index.html")


@login_required
def view_queues(request):
    labels = get_labels(request.user)
    queues = QueueFilter.objects.filter(owner=request.user)
    processed_emails = ProcessedEmail.objects.filter(owner=request.user).order_by(
        "-processed_on"
    )[:5]
    return render(
        request,
        "config/queues.html",
        context={
            "labels": labels,
            "queues": queues,
            "processed_emails": processed_emails,
        },
    )


@login_required
def create_queue(request):
    if not request.user.has_perm("config.add_queue_filter"):
        raise PermissionDenied

    if request.method == "POST":
        label_id = request.POST.get("label_id")
        queue_name = request.POST.get("queue_name")
        if QueueFilter.objects.filter(label_id=label_id).exists():
            messages.add_message(request, messages.ERROR, "Queue already exists")
            return redirect("config:view_queues")

        queue = QueueFilter(
            owner=request.user, label_id=label_id, queue_name=queue_name
        )
        queue.save()

        credentials = pika.PlainCredentials("guest", "guest")
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host="192.168.0.55",
                port=5672,
                virtual_host="/",
                credentials=credentials,
            )
        )
        channel = connection.channel()
        channel.queue_declare(queue=queue_name, durable=True)
        connection.close()

        messages.add_message(request, messages.SUCCESS, f"Queue {queue_name} created!")
        return redirect("config:view_queues")


@login_required
def delete_queue(request, queue_id):
    if not request.user.has_perm("config.delete_queue_filter"):
        raise PermissionDenied

    queue = QueueFilter.objects.get(id=queue_id)
    queue.delete()

    messages.add_message(
        request, messages.SUCCESS, f"Queue {queue.queue_name} deleted!"
    )
    return redirect("config:view_queues")


@login_required
def delete_processed_email(request, email_id):
    if not request.user.has_perm("config.delete_processed_email"):
        raise PermissionDenied

    email = ProcessedEmail.objects.get(id=email_id)
    email.delete()

    messages.add_message(
        request, messages.INFO, f"Email {email.subject} will be reprocessed"
    )
    return redirect("config:view_queues")
