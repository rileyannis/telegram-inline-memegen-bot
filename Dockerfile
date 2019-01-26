# Base image for build
FROM python:3.7.2-alpine3.7
WORKDIR /app

RUN apk add --update python3 \
    python3-dev \
    py-pip \
    build-base

RUN pip3 install --upgrade pip

# install packages
RUN pip3 install -U aiogram
RUN pip3 install ujson
RUN pip3 install uvloop
RUN pip3 install requests

# copy project files
COPY . ./

ENTRYPOINT ["python3", "asyncbot.py"]