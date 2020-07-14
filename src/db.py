from flask_sqlalchemy import SQLAlchemy


"""
The beneath database object should be assigned to the 
flask.Flask application object by calling:
    db.init_app(flask.Flask)
The database object wil on it's turn inherit the Flask
SQLAlchemy configuration parameters as set in the 
flask.Flask application object.
"""

db = SQLAlchemy()
