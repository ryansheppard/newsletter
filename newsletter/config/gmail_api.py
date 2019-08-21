# Taken from https://gist.github.com/imomaliev/0f7fe97d0e736a360cbd17539390b88c
import json
import base64
import pika
from datetime import datetime
from requests import exceptions as requests_errors
from google.auth.exceptions import RefreshError
from google.oauth2.credentials import Credentials as GoogleCredentials
from googleapiclient import discovery
from social_django.utils import load_strategy
from .models import ProcessedEmail


class Credentials(GoogleCredentials):
    """Google auth credentials using python social auth under the hood"""

    def _parse_expiry(self, data):
        """
        Parses the expiry field from a data into a datetime.
        Args:
             data (Mapping): extra_data from UserSocialAuth model
        Returns:
             datetime: The expiration
        """
        return datetime.fromtimestamp(data["auth_time"] + data["expires"])

    def __init__(self, usa):
        """
        Args:
            usa (UserSocialAuth): UserSocialAuth google-oauth2 object
        """
        backend = usa.get_backend_instance(load_strategy())
        data = usa.extra_data
        token = data["access_token"]
        refresh_token = data["refresh_token"]
        token_uri = backend.refresh_token_url()
        client_id, client_secret = backend.get_key_and_secret()
        scopes = backend.get_scope()
        # id_token is not provided with GoogleOAuth2 backend
        super().__init__(
            token,
            refresh_token=refresh_token,
            id_token=None,
            token_uri=token_uri,
            client_id=client_id,
            client_secret=client_secret,
            scopes=scopes,
        )
        self.usa = usa
        # Needed for self.expired() check
        self.expiry = self._parse_expiry(data)

    def refresh(self, request):
        """Refreshes the access token.
        Args:
            request (google.auth.transport.Request): The object used to make
                HTTP requests.
        Raises:
            google.auth.exceptions.RefreshError: If the credentials could
                not be refreshed.
        """
        usa = self.usa
        try:
            usa.refresh_token(load_strategy())
        except requests_errors.HTTPError as e:
            raise RefreshError(e)
        data = usa.extra_data
        self.token = data["access_token"]
        self._refresh_token = data["refresh_token"]
        self.expiry = self._parse_expiry(data)


def get_gmail_service(user):
    usa = user.social_auth.get(provider="google-oauth2")
    service = discovery.build(
        "gmail", "v1", credentials=Credentials(usa), cache_discovery=False
    )
    return service


def get_labels(user):
    service = get_gmail_service(user)
    labels = service.users().labels().list(userId="me").execute()
    return labels.get("labels", [])


def get_emails(user, label_id):
    service = get_gmail_service(user)

    response = (
        service.users()
        .messages()
        .list(userId="me", labelIds=label_id, maxResults=1)
        .execute()
    )
    raw_messages = []
    if "messages" in response:
        raw_messages.extend(response["messages"])

    return raw_messages


def sort_emails(queue, raw_emails):
    service = get_gmail_service(queue.owner)
    messages = []
    for raw_message in raw_emails:
        if ProcessedEmail.objects.filter(email_id=raw_message["id"]).exists():
            continue

        raw_message = (
            service.users().messages().get(userId="me", id=raw_message["id"]).execute()
        )

        headers = raw_message["payload"]["headers"]
        subject = list(filter(lambda header: header["name"] == "Subject", headers))[0][
            "value"
        ]

        if raw_message["payload"]["mimeType"] == "text/plain":
            part = raw_message["payload"]
        else:
            parts = raw_message["payload"]["parts"]
            part = parts[1]

        html = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8")

        message = {"newsletter_title": subject, "queue": queue.queue_name, "html": html}
        messages.append(message)

        processed_email = ProcessedEmail(
            owner=queue.owner,
            email_id=raw_message["id"],
            subject=subject,
            sent_to=queue,
        )
        processed_email.save()

    return messages


def add_email_to_queue(message):
    credentials = pika.PlainCredentials("guest", "guest")
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host="192.168.0.55", port=5672, virtual_host="/", credentials=credentials
        )
    )
    channel = connection.channel()
    serialized_message = json.dumps(message)
    channel.basic_publish(
        exchange="", routing_key=message["queue"], body=serialized_message
    )
