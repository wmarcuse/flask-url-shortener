import os
import json
import pytest

from src.exceptions import InvalidRequestPayload, ShortcodeAlreadyInUse, InvalidShortcode, ShortcodeNotFound

from src.app import create_app, dbs

TEST_CONFIG = {
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///testing.db',
    'TESTING': True
}


@pytest.fixture(name='api_client', scope='class')
def api_client(request):
    app = create_app(config=TEST_CONFIG)
    with app.test_client() as client:
        with app.app_context():
            dbs.init_app(app=app)
        request.cls.api_client = client
        yield client
        del client
        del request.cls.api_client


def remove_test_database():
    os.remove(os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'src') + r'\testing.db')


@pytest.mark.usefixtures('api_client')
class TestShortenUrl:
    def test_shorten_url_providing_url_success(self):
        request = self.api_client.post(
            path='/shorten',
            data=json.dumps({'url': 'http://example1.com'}),
            headers={'Content-Type': 'application/json'}
        )
        assert 201 == request.status_code
        response = request.get_json()
        assert 'shortcode' in response

    def test_shorten_url_providing_invalid_json_failure(self):
        request = self.api_client.post(
            path='/shorten',
            data={'url': 'http://example.com'}
        )
        assert InvalidRequestPayload.STATUS_CODE == request.status_code
        response = request.get_json()
        assert 'Invalid JSON' in response['message']

    def test_shorten_url_not_providing_url_failure(self):
        request = self.api_client.post(
            path='/shorten',
            data=json.dumps({'x': 'xyz'}),
            headers={'Content-Type': 'application/json'}
        )
        assert InvalidRequestPayload.STATUS_CODE == request.status_code
        response = request.get_json()
        assert 'Url not present' in response['message']

    def test_shorten_url_providing_url_and_shortcode_success(self):
        url = 'http://example2.com'
        shortcode = '01_2qp'
        request = self.api_client.post(
            path='/shorten',
            data=json.dumps({'url': url, 'shortcode': shortcode}),
            headers={'Content-Type': 'application/json'}
        )
        assert 201 == request.status_code
        response = request.get_json()
        assert shortcode == response['shortcode']

    def test_shorten_url_shortcode_already_in_use_failure(self):
        url = 'http://example3.com'
        shortcode = '01_2qp'
        request = self.api_client.post(
            path='/shorten',
            data=json.dumps({'url': url, 'shortcode': shortcode}),
            headers={'Content-Type': 'application/json'}
        )
        assert ShortcodeAlreadyInUse.STATUS_CODE == request.status_code
        response = request.get_json()
        assert ShortcodeAlreadyInUse.MESSAGE in response['message']

    def test_shorten_url_shortcode_invalid_failure(self):
        url = 'http://example4.com'
        shortcode = 'xy_'
        request = self.api_client.post(
            path='/shorten',
            data=json.dumps({'url': url, 'shortcode': shortcode}),
            headers={'Content-Type': 'application/json'}
        )
        assert InvalidShortcode.STATUS_CODE == request.status_code
        response = request.get_json()
        assert InvalidShortcode.MESSAGE in response['message']

    def teardown_class(self):
        remove_test_database()


@pytest.mark.usefixtures('api_client')
class TestGetUrl:
    URL = 'http://example5.com'
    SHORTCODE = 'lsi821'

    def setup_method(self):
        request = self.api_client.post(
            path='/shorten',
            data=json.dumps({'url': self.URL, 'shortcode': self.SHORTCODE}),
            headers={'Content-Type': 'application/json'}
        )
        assert request.status_code == 201

    def test_get_url_success(self):
        request = self.api_client.get(
            path='/{SHORTCODE}'.format(SHORTCODE=self.SHORTCODE)
        )
        assert request.status_code == 302
        assert request.headers['Location'] == self.URL

    def test_get_url_shortcode_not_found_failure(self):
        request = self.api_client.get(
            path='/{SHORTCODE}'.format(SHORTCODE=self.SHORTCODE + 'x')
        )
        assert request.status_code == ShortcodeNotFound.STATUS_CODE
        response = request.get_json()
        assert response['message'] == ShortcodeNotFound.MESSAGE

    def teardown_class(self):
        remove_test_database()


@pytest.mark.usefixtures('api_client')
class TestGetStats:
    URL = 'http://example6.com'
    SHORTCODE = 'x0_q23'

    def setup_method(self):
        request = self.api_client.post(
            path='/shorten',
            data=json.dumps({'url': self.URL, 'shortcode': self.SHORTCODE}),
            headers={'Content-Type': 'application/json'}
        )
        assert request.status_code == 201

    def test_get_stats_success(self):
        request = self.api_client.get(
            path='/{SHORTCODE}/stats'.format(SHORTCODE=self.SHORTCODE)
        )
        assert request.status_code == 200
        response = request.get_json()
        assert 'created' in response
        assert 'lastRedirect' in response
        assert 'redirectCount' in response

    def test_get_stats_shortcode_not_found_failure(self):
        request = self.api_client.get(
            path='/{SHORTCODE}/stats'.format(SHORTCODE=self.SHORTCODE + 'x')
        )
        assert request.status_code == ShortcodeNotFound.STATUS_CODE
        response = request.get_json()
        assert response['message'] == ShortcodeNotFound.MESSAGE

    def teardown_class(self):
        remove_test_database()