# Используйте официальный образ Python
FROM python:3.9-slim

# Установите pip
RUN apt-get update \
    && apt-get install -y python3-pip

# Установите FastAPI и Uvicorn
RUN pip3 install fastapi uvicorn openpyxl python-multipart


# Копируйте ваше FastAPI приложение в контейнер
COPY ./main.py /app/main.py


# Запустите Uvicorn для FastAPI приложения
#CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
