ARG PYTHON_VERSION="3.10"
FROM harbor.devops.k8s.rcsb.org/dockerhub/python:$PYTHON_VERSION-slim-bookworm AS build-image
WORKDIR /app/

# Copy project files (dependencies should include selected versions of uvicorn gunicorn)
COPY pyproject.toml /app/
COPY . /app/

RUN apt-get update && apt-get install -y --no-install-recommends build-essential=12.9 \
    libcairo2=1.16.0-7 \
    && pip install --no-cache-dir --upgrade pip==25.0.1 cmake==3.27.0 hatch==1.16.2 wheel==0.45.1 setuptools==80.9.0 \
    && hatch run pip install --no-cache-dir .

FROM harbor.devops.k8s.rcsb.org/dockerhub/python:$PYTHON_VERSION-slim-bookworm AS runtime-image
LABEL maintainer="RCSB IT <it@rcsb.org>"

WORKDIR /app/

# Make sure scripts in .local are usable:
ENV PATH=/home/ubuntu/.local/bin:$PATH
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y --no-install-recommends libcairo2=1.16.0-7 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && adduser --disabled-password --gecos '' ubuntu \
    && chown -R ubuntu /app

COPY --from=build-image --chown=ubuntu:ubuntu /root/.local /home/ubuntu/.local
COPY --chown=ubuntu:ubuntu ./rcsb /app/rcsb

USER ubuntu

# Launch the service
ENTRYPOINT ["gunicorn", "rcsb.app.chem.main:app"]
