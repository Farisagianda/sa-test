FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# copy lock/requirements first so the layer can be cached
COPY requirements.txt /tmp/requirements.txt

# use buildx cache mount so pip can reuse wheel downloads between builds
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip \
 && pip install --no-warn-script-location -r /tmp/requirements.txt

# copy only the runtime code (exclude files/folders via .dockerignore)
COPY . .

# run as non-root
USER 65532:65532

EXPOSE 8080
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8080"]