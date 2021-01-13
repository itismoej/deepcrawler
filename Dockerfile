FROM python:3.9

ENV PYTHONUNBUFFERED 1

RUN mkdir /app
COPY . /app/
WORKDIR /app

RUN pip install -r requirements.txt
RUN chmod +x ./entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]

EXPOSE 8000