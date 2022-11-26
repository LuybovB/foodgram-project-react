FROM python:3.8.6-slim

WORKDIR /backend

COPY . .

RUN pip3 install -r requirements.txt --no-cache-dir

COPY . .

EXPOSE 8000

CMD ["gunicorn", "backend.wsgi:application", "--bind", "0:8000"]
