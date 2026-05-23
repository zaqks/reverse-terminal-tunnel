FROM python:3.12-slim

RUN pip install uv
RUN uv pip install --system -r requirements.txt

RUN apt update
RUN apt install patchelf binutils build-essential
