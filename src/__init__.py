# from flask import Flask
# import os
# from flask_sqlalchemy import SQLAlchemy
#
# from app_config import FlaskConfig
# # from endpoints import blueprint_shorten_url
#
# _APP_CONFIG = {
#     **FlaskConfig.CONFIG_FLASK,
#     **FlaskConfig.CONFIG_SQLALCHEMY,
# }
#
# db = SQLAlchemy()
#
# def create_app(config=_APP_CONFIG):
#     app = Flask(__name__)
#
#     # load app specified configuration
#     if config is not None:
#         if isinstance(config, dict):
#             app.config.update(config)
#         elif config.endswith('.py'):
#             app.config.from_pyfile(config)
#
#     db.init_app(app=app)
#     # db.create_all(app=app)
#     # app.app_context().push()
#
#     with app.app_context():
#         import endpoints
#         db.create_all()
#
#     app.register_blueprint(blueprint=endpoints.blueprint_shorten_url, url_prefix="")
#
#     return app
#
#
# if __name__ == "__main__":
#     ENVIRONMENT_DEBUG = os.environ.get("APP_DEBUG", True)
#     ENVIRONMENT_PORT = os.environ.get("APP_PORT", 5000)
#     create_app(_APP_CONFIG).run(host='0.0.0.0', port=ENVIRONMENT_PORT, debug=ENVIRONMENT_DEBUG)