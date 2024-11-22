FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1

RUN apt-get update -y
RUN apt-get install sqlite3

RUN pip install --upgrade pip
RUN pip install uv

WORKDIR /code
COPY ./pyproject.toml .

RUN uv pip install --system -r ./pyproject.toml

COPY . .
RUN uv pip install --system .

RUN chmod +x ./docker_entrypoint.sh
ENTRYPOINT ["./docker_entrypoint.sh"]

