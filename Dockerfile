FROM python:3.8-slim
ENV PYTHONUNBUFFERED 1

RUN apt-get update -y
RUN apt-get install -y git

RUN mkdir /code
WORKDIR /code
COPY . /code/

RUN pip install -r requirements.txt
RUN pip install -e .

