FROM python:alpine

WORKDIR /usr/src/app

EXPOSE 5000

RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP roundbroker

CMD ["flask", "run", "-h", "0.0.0.0", "-p", "5000"]
