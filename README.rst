URL shortening with Flask
=========================

|Status| |Python versions| |Build status| |Coverage| |License|

This is an URL shortening REST API built with Python and Flask.

Installation
------------

Create a virtual environment and install teh requirements

    pip install requirements.txt

Run the app
-----------

To run the app locally, either open your favourite IDE and run `app.py`, or set the `src` directory as your current
working directory and run

    python app.py

Test the app
------------

To test the app, install pytest in your virtual environment, as pytest is a development/CI-CD requirement only it is not
available in the requirements manifest

    pip install pytest

To run the tests, set the `tests` directory as you current working directory and run

    pytest -s