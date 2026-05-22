FROM python:3.12

WORKDIR /app
COPY . .

RUN pip install uv
RUN uv pip install -r requirements


EXPOSE 7860

CMD [ "python3" , "relay.py"]