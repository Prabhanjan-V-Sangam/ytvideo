FROM python:3.11-alpine

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apk update && apk add --no-cache \
    bash \
    build-base \
    gcc \
    libc-dev \
    glib-dev \
    gobject-introspection-dev \
    py3-gobject3 \
    gstreamer \
    gstreamer-dev \
    gst-plugins-base \
    gst-plugins-good \
    gst-plugins-bad \
    gst-plugins-ugly \
    gst-libav \
    orc \
    libintl \
    libffi-dev \
    openssl-dev \
    && rm -rf /var/cache/apk/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
