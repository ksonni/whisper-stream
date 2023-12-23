FROM python:3.11-bullseye

RUN apt-get update && apt-get install --assume-yes ffmpeg

WORKDIR /usr/src/app

COPY requirements.txt .
COPY Makefile .

RUN make install

COPY . .

CMD [ "python", "./server.py" ]
