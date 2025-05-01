FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Создание директории для базы данных
RUN mkdir -p instance

# Установка разрешений
RUN chmod -R 755 .

# Открываем порт, который будет использовать Flask
EXPOSE 5000

# Запуск приложения
ENV FLASK_APP=run.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

CMD ["python", "run.py"] 