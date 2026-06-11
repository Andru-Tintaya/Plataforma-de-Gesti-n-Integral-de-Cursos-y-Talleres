import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'asistencia-uni-2026'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///asistencia.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False