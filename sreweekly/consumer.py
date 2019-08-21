import os
import json
import pika
from bs4 import BeautifulSoup
import slack


SLACK_API_TOKEN = os.environ.get("SLACK_API_TOKEN")
SLACK_CHANNEL = os.environ.get("SLACK_CHANNEL")
RABBITMQ_USERNAME = os.environ.get("RABBITMQ_USERNAME")
RABBITMQ_PASSWORD = os.environ.get("RABBITMQ_PASSWORD")
RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST")
RABBITMQ_PORT = os.environ.get("RABBITMQ_PORT")


class Consumer:
    def __init__(self, queue):
        self.queue = queue

    def consume(self):
        print("Building connection")
        credentials = pika.PlainCredentials(RABBITMQ_USERNAME, RABBITMQ_PASSWORD)
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=RABBITMQ_HOST,
                port=RABBITMQ_PORT,
                virtual_host="/",
                credentials=credentials,
            )
        )
        channel = connection.channel()

        print("Listening for messages")
        for method_frame, _, body in channel.consume(f"{self.queue}"):
            channel.basic_ack(method_frame.delivery_tag)
            message = json.loads(body)
            print(f"Processing {message['newsletter_title']}")
            self.parse_message(message)

        channel.cancel()
        connection.close()

    def parse_message(self, message):
        pass


class SreWeeklyConsumer(Consumer):
    def __init__(self, queue, slack_token, slack_channel):
        super().__init__(queue)
        self.slack_token = slack_token
        self.slack_channel = slack_channel

    def parse_message(self, message):
        soup = BeautifulSoup(message["html"], "html.parser")
        entries = soup.find_all("div", class_="sreweekly-entry")
        attachments = []
        for entry in entries:
            title = entry.find("div", class_="sreweekly-title").text
            link = entry.find("a").get("href")
            desc_div = entry.find("div", class_="sreweekly-description")
            desc_text = desc_div.find_all("p")
            desc = desc_text[0].text
            if len(desc_text) > 1:
                author = desc_text[1].text
            else:
                author = ""
            attachment = {
                "title": title,
                "title_link": link,
                "text": desc,
                "footer": author,
            }
            attachments.append(attachment)

        client = slack.WebClient(token=self.slack_token)
        client.chat_postMessage(
            channel=self.slack_channel,
            text=f"*{message['newsletter_title']}*",
            attachments=attachments,
        )

        print(f"Sent {message['newsletter_title']} to {self.slack_channel}")


def main():
    consumer = SreWeeklyConsumer("sreweekly", SLACK_API_TOKEN, SLACK_CHANNEL)
    consumer.consume()


if __name__ == "__main__":
    main()
