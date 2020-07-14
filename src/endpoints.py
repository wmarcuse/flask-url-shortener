from flask import Blueprint, request, jsonify

from models import Url, Redirect, Stat
from exceptions import InvalidRequestPayload

import logging

LOGGER = logging.getLogger(__name__)

blueprint_shorten_url = Blueprint('shorten_url', __name__)
blueprint_get_url = Blueprint('get_url', __name__)
blueprint_get_stats = Blueprint('get_stats', __name__)


@blueprint_shorten_url.route('/shorten', methods=['POST'])
def shorten_url():
    """
    This endpoint method handles the url shortening requests,
    routed to the configured relative routing url and being
    a POST request.

    The Url database model specific methods will handle the logic.

    :raises:
        InvalidRequestPayload: When the provided payload is invalid JSON.
        InvalidRequestPayload: When the provided payload does not contain
            the url to shorten.

    :return: The shortened url and corresponding shortcode.
    :rtype: flask.Response

    .. note::
        Note that if no shortcode is provided in the request payload, the
        shortcode is set to None, the Shortcode database model specific
        methods will handle the logic.
    """
    if not request.is_json:
        raise InvalidRequestPayload('Unsupported Media Type: Invalid JSON')
    request_data = request.get_json()
    if 'url' not in request_data:
        raise InvalidRequestPayload('Url not present')
    request_url = request_data['url']
    if 'shortcode' not in request_data:
        request_shortcode = None
    else:
        request_shortcode = request_data['shortcode']

    shortcode = Url.insert_url(url=request_url, shortcode=request_shortcode)
    response = jsonify({
        "shortcode": shortcode
    })
    response.status_code = 201
    return response


@blueprint_get_url.route('/<shortcode>', methods=['GET'])
def get_url(shortcode):
    """
    This endpoint method handles the redirect requests,
    routed to the shortcode specific routing url and being
    a GET request.

    The Redirect database model specific methods will handle the logic.

    :param shortcode: The provided shortcode as url parameter.
    :type shortcode: str

    :return: The response with the corresponding url for the provided
        shortcode added to the Location header.
    :rtype: flask.Response

    .. note::
        The Redirect database model specific methods handle the logic
        and exception handling for this endpoint, as the endpoint relies
        heavily on database specific logic.
    .. seealso::
        See for database model related methods: src/models.py
        See for exception related exceptions: src/exceptions.py
    """
    redirect_url = Redirect.redirect(shortcode=shortcode)
    response = jsonify()
    response.status_code = 302
    response.headers['Location'] = redirect_url
    return response


@blueprint_get_stats.route('/<shortcode>/stats', methods=['GET'])
def get_stats(shortcode):
    """
    This endpoint method handles the shortcode stats requests,
    routed to the shortcode specific routing url concatenated with
    the stats endpoint and being a GET request.

    The Stat database model specific methods will handle the logic.

    :param shortcode: The provided shortcode as url parameter.
    :type shortcode: str

    :return: The response with the corresponding stats details for the
        provided shortcode.
    :rtype: flask.Response

    .. note::
        The Stat database model specific methods handle the logic
        and exception handling for this endpoint, as the endpoint relies
        heavily on database specific logic.
    .. seealso::
        See for database model related methods: src/models.py
        See for exception related exceptions: src/exceptions.py
    """
    stats = Stat.get_stats(shortcode=shortcode)
    response = jsonify(stats)
    response.status_code = 200
    return response
