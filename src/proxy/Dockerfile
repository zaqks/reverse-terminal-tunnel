FROM python:3.12

WORKDIR /app

COPY requirements.txt .
RUN pip install uv
RUN uv pip install -r requirements.txt

COPY relay.py .

EXPOSE 7860

CMD [ "python3" , "relay.py"]