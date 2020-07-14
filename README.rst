URL shortening with Flask
=========================

|Python versions| |Build status| |Coverage| |License|

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


.. |Python versions| image:: https://img.shields.io/pypi/pyversions/pokeman

.. |Build Status| image:: https://api.travis-ci.org/wmarcuse/flask-url-shortener.png?branch=master
  :target: https://travis-ci.org/github/wmarcuse/flask-url-shortener

.. |Coverage| image:: https://codecov.io/gh/wmarcuse/flask-url-shortener/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/wmarcuse/flask-url-shortener

.. |License| image:: https://img.shields.io/github/license/wmarcuse/flask-url-shortener
  :target: https://github.com/wmarcuse/flask-url-shortener