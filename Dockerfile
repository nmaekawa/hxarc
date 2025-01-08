FROM python:3.12-bookworm AS build

RUN apt-get update -y

RUN pip install --upgrade pip
RUN pip install uv

WORKDIR /code

RUN uv venv --python 3.12 /venv
ENV PATH=/venv/bin:$PATH VIRTUAL_ENV=/venv

COPY ./pyproject.toml .
RUN uv pip install -r ./pyproject.toml

COPY . .
RUN uv pip install .

# cleanup appuser
RUN rm -rf /home/appuser && mkdir /home/appuser

# keep entrypoint
COPY ./manage.py ./docker_entrypoint.sh ./docker_dotenv.env ./wait-for-it.sh /home/appuser

ENTRYPOINT []
CMD ["/bin/bash"]


FROM python:3.12-slim-bookworm AS runtime

RUN export DEBIAN_FRONTEND=noninteractive && \
    apt-get update && \
    apt-get install --yes --no-install-recommends procps tini && \
    # cleanup
    apt-get clean && rm -rf /var/lib/apt/lists/*

# non-privileged user
RUN useradd --create-home appuser
WORKDIR /home/appuser
USER appuser

# app needs other dirs
RUN mkdir /home/appuser/media /home/appuser/static

# copy only venv from buird image
COPY --from=build --chown=appuser:appuser /venv /venv

# activate venv
ENV PATH=/venv/bin:$PATH VIRTUAL_ENV=/venv

# if program crashes, try to record traceback
# https://docs.python.org/3/library/faulthandlers.html
ENV PYTHONFAULTHANDLER=true

# copy application code
COPY --from=build --chown=appuser:appuser /home/appuser /home/appuser

ENTRYPOINT ["tini", "-g", "--"]
#CMD ["/bin/bash", "/home/appuser/docker_entrypoint.sh"]
CMD ["/bin/bash", "./wait-for-it.sh", "db:5432", "--", "./docker_entrypoint.sh"]
