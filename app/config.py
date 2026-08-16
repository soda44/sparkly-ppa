import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @property
    def SQLALCHEMY_DATABASE_URI(self):
        """Lida a cada criação de app, permitindo trocar o banco (ex.: testes)."""
        return os.getenv('DATABASE_URL', 'sqlite:///sparkly.db')
