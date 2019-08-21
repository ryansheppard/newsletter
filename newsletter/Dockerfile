FROM python:3.7.4-alpine3.10

RUN mkdir /app/
COPY . /app/
WORKDIR /app/
RUN ls
RUN ls config
RUN pip install -r requirements.txt

ENTRYPOINT ["python", "-u",  "manage.py", "runserver"]
