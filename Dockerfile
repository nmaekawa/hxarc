FROM python:3.12-slim-bookworm
ENV PYTHONUNBUFFERED=1

RUN apt-get update -y && apt-get -y upgrade
RUN apt-get install sqlite3

RUN pip install --upgrade pip

# run as non-root user
RUN useradd --create-home hxarc
USER hxarc

# volume with subprocs
VOLUME /subproc

# setup hx_util
RUN mkdir /subproc/hx_util
WORKDIR /subproc/hx_util

RUN python3 -m venv ./venv
COPY ../work/hxarc-upgrade/subprocs/hx_util ./hx_util

RUN ./venv/bin/pip install -r ./requirements.txt
RUN ./venv/bin/pip install .

# web app
WORKDIR /code
COPY . .
RUN pip install .

VOLUME /data

#RUN chmod +x ./docker_entrypoint.sh
ENTRYPOINT ["./docker_entrypoint.sh"]

