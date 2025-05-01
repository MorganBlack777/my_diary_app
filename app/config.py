import os
from dotenv import load_dotenv

load_dotenv()  # Загружает переменные из .env

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY') or 'your-secret-key-here'
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or 'sqlite:///C:\\users\\playi\\onedrive\\рабочий стол\\my_diary_app\\diary.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False