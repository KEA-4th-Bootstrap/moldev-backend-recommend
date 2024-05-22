FROM python:3.9.6

COPY ./requirements.txt /requirements.txt
COPY ./app /app
COPY ./core /core
COPY ./config.py /config.py

RUN pip3 install  --no-cache-dir -r /requirements.txt

CMD ["uvicorn", "app.server:app", "--host", "0.0.0.0"]