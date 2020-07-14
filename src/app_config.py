class FlaskConfig:
    """
    This object contains the configuration parameters for the flask.Flask
    application object. General package specific configuration
    parameters are here stored as well for clarity purposes,
    i.e. Flask_SQLAlchemy configuration parameters
    """
    CONFIG_FLASK = {
        "SECRET_KEY": "my_secret_key"
    }

    SQLITE_URI = 'sqlite:///test.db'

    CONFIG_SQLALCHEMY = {
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SQLALCHEMY_DATABASE_URI': SQLITE_URI
    }
