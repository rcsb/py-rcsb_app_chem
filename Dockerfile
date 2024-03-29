FROM python:3.9-slim AS build-image

WORKDIR /app/

# copy requirements file (should include selected versions of uvicorn gunicorn)
COPY ./requirements.txt /app/requirements.txt

RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
    libcairo2 \
    && pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir --user -r /app/requirements.txt

FROM python:3.9-slim AS runtime-image
LABEL maintainer="RCSB IT <it@rcsb.org>"

WORKDIR /app/

# Make sure scripts in .local are usable:
ENV PATH=/home/ubuntu/.local/bin:$PATH
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN adduser --disabled-password --gecos '' ubuntu \
    && chown -R ubuntu /app

COPY --from=build-image --chown=ubuntu:ubuntu /root/.local /home/ubuntu/.local
COPY --chown=ubuntu:ubuntu ./scripts/gunicorn_conf.py /app/gunicorn_conf.py
COPY --chown=ubuntu:ubuntu ./scripts/LAUNCH_GUNICORN.sh /app/launch.sh
COPY --chown=ubuntu:ubuntu ./rcsb /app/rcsb

USER ubuntu

# Launch the service
CMD ["/app/launch.sh"]