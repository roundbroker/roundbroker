FROM python:alpine

WORKDIR /usr/src/app

EXPOSE 5000

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP turntable

CMD ["flask", "run", "-h", "0.0.0.0", "-p", "5000"]
