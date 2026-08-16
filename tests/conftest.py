import os
import pytest

from app import create_app
from app.models import db


@pytest.fixture()
def app(tmp_path):
    """App Flask com banco SQLite isolado em arquivo temporário."""
    os.environ['DATABASE_URL'] = f"sqlite:///{tmp_path / 'test.db'}"
    application = create_app()
    yield application


@pytest.fixture()
def ctx(app):
    """Contexto da aplicação com o banco recriado do zero."""
    with app.app_context():
        db.drop_all()
        db.create_all()
        yield
