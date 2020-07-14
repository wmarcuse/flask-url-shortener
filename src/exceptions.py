from abc import ABC
from flask import jsonify


class AbstractHttpException(ABC, Exception):
    """
    The abstract base class for API related exceptions.

    This Exception base class is used for providing an
    API client with a specific error message and a HTTP
    status code.
    """
    def __init__(self, *args, payload=None,):
        """
        This method initializes the Exception object with
        the provided parameters, if provided.

        The *args parameter is for providing an Exception
        message as native Python Exceptions do as well, by
        providing an unnamed first parameter.

        :param args: The provided, unnamed Exception message.
        :type args: str

        :param payload: The provided optional payload for the
            flask.Response.
        :type payload: dict
        """
        if args:
            self._message = args[0]
        else:
            self._message = self.MESSAGE
        self.statement = '{EXCEPTION}: {MESSAGE}'.format(
            EXCEPTION=self.__class__.__name__,
            MESSAGE=self._message
        )
        self.payload = payload

    @classmethod
    def __init_subclass__(cls):
        """
        This method initializes the subclass object first, in
        order to determine if the required attributes are set.

        :raises:
            NotImplementedError: Is raised when a required attribute is
                missing in the subclass.
        """
        required_attributes = [
            'STATUS_CODE',
            'MESSAGE'
        ]
        for attr in required_attributes:
            if not hasattr(cls, attr):
                raise NotImplementedError(  # pragma: no cover
                    '{EXCEPTION} cannot be instantiated without: {PARAM}'.format(  # pragma: no cover
                        EXCEPTION=cls.__name__,  # pragma: no cover
                        PARAM=attr  # pragma: no cover
                    ))  # pragma: no cover

    def http_response(self):
        """
        This method creates a HTTP response package from
        the provided parameters.

        :return: The HTTP response package.
        :rtype: flask.Response
        """
        response = dict(self.payload or ())
        response['message'] = self._message
        http_package = jsonify(response)
        http_package.status_code = self.STATUS_CODE
        return http_package

    def __str__(self):
        """For development purposes"""
        return self.statement  # pragma: no cover


class InvalidRequestPayload(AbstractHttpException):
    """This Exception should be used when the incoming request payload is invalid"""
    STATUS_CODE = 400
    MESSAGE = 'The provided request payload is invalid'


class ShortcodeAlreadyInUse(AbstractHttpException):
    """This Exception should be used when the provided shortcode by the client is already in use"""
    STATUS_CODE = 409
    MESSAGE = 'Shortcode already in use'


class ShortcodeNotFound(AbstractHttpException):
    """This Exception should be used when the provided shortcode by the client doe not exist"""
    STATUS_CODE = 404
    MESSAGE = 'Shortcode not found'


class InvalidShortcode(AbstractHttpException):
    """This Exception should be used when the provided shortcode by the client has an invalid format"""
    STATUS_CODE = 412
    MESSAGE = 'The provided shortcode is invalid'
