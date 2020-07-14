import pytest

from . import TestAttributes as TA

from flask import Flask
from sqlalchemy.exc import OperationalError

from src.app import create_app, blueprint_get_stats, blueprint_get_url, blueprint_shorten_url
from exceptions import InvalidRequestPayload, ShortcodeAlreadyInUse, ShortcodeNotFound, InvalidShortcode


TEST_CONFIG = {
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///testing.db',
    'TESTING': True
}


@pytest.fixture(name='app_instance', scope='class')
def app_instance(request):
    app = create_app(config=TEST_CONFIG)
    request.cls.app = app
    yield app
    del app
    del request.cls.app


@pytest.mark.usefixtures('app_instance')
class TestCreateApp:
    class DbsMock:
        def __init__(self):
            self.session = self.Session

        @classmethod
        def init_app(cls, app):
            pass

        class Session:
            @classmethod
            def commit(cls):
                pass

        @classmethod
        def create_all(cls, app=None):
            if isinstance(app, Flask):
                raise OperationalError(statement=None, params=None, orig=None)
            if app is None:
                pass

    def test_base_instance(self):
        assert isinstance(self.app, Flask)

    def test_create_app_dbs_create_all_OperationalError_exception(self):
        from src import app  # avoid top-level import colision
        with TA.patch(app, 'dbs', self.DbsMock()):
            app = create_app(config=TEST_CONFIG)
            assert True

    def test_blueprints_present(self):
        assert blueprint_get_url in self.app.blueprints.values()
        assert blueprint_shorten_url in self.app.blueprints.values()
        assert blueprint_get_stats in self.app.blueprints.values()

    def test_error_handlers_present(self):
        assert InvalidShortcode.__name__ in str(self.app.error_handler_spec)
        assert InvalidRequestPayload.__name__ in str(self.app.error_handler_spec)
        assert ShortcodeAlreadyInUse.__name__ in str(self.app.error_handler_spec)
        assert ShortcodeNotFound.__name__ in str(self.app.error_handler_spec)
