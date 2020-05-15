FROM python:3.8.3-alpine3.10

RUN mkdir /app/
COPY . /app/
WORKDIR /app/
RUN pip install -r requirements.txt

ENTRYPOINT ["python", "-u",  "manage.py", "runserver"]
