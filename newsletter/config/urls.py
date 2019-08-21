from django.urls import path

from . import views

app_name = "config"

urlpatterns = [
    path("", views.index, name="index"),
    path("queue", views.view_queues, name="view_queues"),
    path("queue/create/", views.create_queue, name="create_queue"),
    path("queue/<int:queue_id>/delete/", views.delete_queue, name="delete_queue"),
    path(
        "email/<int:email_id>/delete/",
        views.delete_processed_email,
        name="delete_processed_email",
    ),
]
