FROM python:3.7.4-alpine3.10

RUN mkdir /app/
COPY requirements.txt /app/
COPY consumer.py /app/
WORKDIR /app/
RUN pip install -r requirements.txt

ENTRYPOINT ["python",  "-u", "consumer.py"]
