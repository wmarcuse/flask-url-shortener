from flask import Flask
import os
from sqlalchemy.exc import OperationalError

from db import db as dbs
from app_config import FlaskConfig
from exceptions import InvalidRequestPayload, ShortcodeAlreadyInUse, ShortcodeNotFound, InvalidShortcode
from endpoints import blueprint_shorten_url, blueprint_get_url, blueprint_get_stats

APP_CONFIG = {
    **FlaskConfig.CONFIG_FLASK,
    **FlaskConfig.CONFIG_SQLALCHEMY,
}


def create_app(config):
    """
    This method instantiates the Flask app.

    The method alters the application object for the
    desired url shortening purpose, by:

    - Configuring the application object with the provided
      configuration parameters.
    - Attaching the SQLAlchemy database object to the
      application object.
    - Configuring the database.
    - Registering the modular blueprints on the application
      object.
    - Configuring a custom error handler for various
      exception scenario's.

    :param config: The provided configuration parameters.
    :type config: dict

    :return: The application object.
    :rtype: flask.Flask
    """
    app = Flask(__name__)

    if config is not None and isinstance(config, dict):
        app.config.update(config)

    dbs.init_app(app=app)

    try:
        dbs.create_all(app=app)
    except OperationalError as exc:
        from models import Url, Shortcode, Stat, Redirect
        dbs.create_all()
        dbs.session.commit()

    app.register_blueprint(blueprint=blueprint_shorten_url, url_prefix='')
    app.register_blueprint(blueprint=blueprint_get_url, url_prefix='')
    app.register_blueprint(blueprint=blueprint_get_stats, url_prefix='')

    exceptions = [
        InvalidRequestPayload,
        ShortcodeAlreadyInUse,
        ShortcodeNotFound,
        InvalidShortcode
    ]

    for exception in exceptions:
        @app.errorhandler(exception)
        def handle_exception(error):
            return error.http_response()

    return app


if __name__ == '__main__':
    ENVIRONMENT_DEBUG = os.environ.get('APP_DEBUG', True)  # pragma: no cover
    ENVIRONMENT_PORT = os.environ.get('APP_PORT', 5000)  # pragma: no cover
    create_app(APP_CONFIG).run(host='0.0.0.0', port=ENVIRONMENT_PORT, debug=ENVIRONMENT_DEBUG)  # pragma: no cover
