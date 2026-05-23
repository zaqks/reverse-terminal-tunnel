FROM python:3.12-slim

COPY requirements.txt .
RUN pip install uv
RUN uv pip install --system -r requirements.txt

RUN apt-get update
RUN apt-get install -y patchelf binutils build-essential