FROM python:3.11-bullseye

RUN apt-get update && apt-get install --assume-yes ffmpeg

RUN apt-get install --assume-yes protobuf-compiler

WORKDIR /usr/src/app

RUN curl https://get.volta.sh | bash
RUN volta install node@20

RUN npm install -g protoc-gen-ts

COPY requirements.txt .
COPY Makefile .

RUN make install

COPY . .

CMD [ "make", "run" ]
