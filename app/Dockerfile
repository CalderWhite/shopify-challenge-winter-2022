FROM python:3.9-slim

# Install first so we don't reinstall everything on every build

COPY requirements.txt requirements.txt

RUN apt-get update && apt-get install -y libpq-dev gcc
RUN pip install -r requirements.txt

WORKDIR /opt/shopify-challenge

COPY . .

ENTRYPOINT [ "python3", "server.py" ]
