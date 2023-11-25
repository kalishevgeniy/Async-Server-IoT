FROM python:3.11
LABEL creator="https://github.com/kalishevgeniy"

WORKDIR /var/lib/server/async_server_iot

COPY ../main.py /var/lib/server
COPY /src /var/lib/server/async_server_iot

RUN pip3 install --no-cache-dir -r requirements.txt

WORKDIR /var/lib/server
