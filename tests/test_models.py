import os
import pytest
from unittest import mock

from . import TestAttributes as TA

from sqlalchemy.exc import IntegrityError
from src.exceptions import InvalidRequestPayload, ShortcodeAlreadyInUse, InvalidShortcode, ShortcodeNotFound
from models import Url, Shortcode, Stat, Redirect
from src.app import create_app, dbs

TEST_CONFIG = {
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///testing.db',
    'TESTING': True
}


@pytest.fixture(name='app', scope='class')
def app(request):
    app = create_app(config=TEST_CONFIG)
    with app.app_context():
        dbs.init_app(app=app)
        request.cls.app = app
        yield app
        del app


def remove_test_database():
    os.remove(os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'src') + r'/testing.db')


@pytest.mark.usefixtures('app')
class TestUrlModel:

    def test_base_name(self):
        assert Url.__name__ == 'Url'

    def test_url_insert_new_without_shortcode_success(self):
        with self.app.app_context():
            url = Url.insert_url(url='scenario1.com')
            assert Shortcode.check_validity(shortcode=url)

    def test_url_insert_new_with_shortcode_success(self):
        with self.app.app_context():
            url = Url.insert_url(url='scenario2.com', shortcode='js9_86')
            assert Shortcode.check_validity(shortcode=url)
            assert url == 'js9_86'

    def test_url_insert_existing_without_shortcode_success(self):
        with self.app.app_context():
            url = Url.insert_url(url='scenario2.com')
            assert Shortcode.check_validity(shortcode=url)
            assert url == 'js9_86'

    def test_url_insert_existing_with_shortcode_success(self):
        with self.app.app_context():
            url = Url.insert_url(url='scenario2.com', shortcode='js9_86')
            assert Shortcode.check_validity(shortcode=url)
            assert url == 'js9_86'

    def test_url_insert_nullable_failure(self):
        with self.app.app_context():
            with pytest.raises(IntegrityError):
                url = Url.insert_url(url=None)

    def test_url_insert_new_already_in_use_shortcode_failure(self):
        with self.app.app_context():
            with pytest.raises(Exception) as exc:  # Wide catch, scope narrowed for preventing nested Exception override
                url = Url.insert_url(url='scenario3.com', shortcode='js9_86')
            assert isinstance(exc.type, ShortcodeAlreadyInUse.__class__)  # Sanity check

    def test_url_insert_new_invalid_format_shortcode_failure(self):
        with self.app.app_context():
            with pytest.raises(Exception) as exc:  # Wide catch, scope narrowed for preventing nested Exception override
                url = Url.insert_url(url='scenario4.com', shortcode='xop')
            assert isinstance(exc.type, InvalidShortcode.__class__)  # Sanity check

    def teardown_class(self):
        remove_test_database()


@pytest.mark.usefixtures('app')
class TestShortcodeModel:

    def test_base_name(self):
        assert Shortcode.__name__ == 'Shortcode'

    def test_generate_random(self):
        random_string = Shortcode.generate_random()
        assert Shortcode.check_validity(shortcode=random_string)

    def test_check_validity_success(self):
        assert Shortcode.check_validity(shortcode='927hs_')

    def test_check_validity_failure(self):
        assert Shortcode.check_validity(shortcode='poc') is False

    def test_check_in_use_true(self):
        Url.insert_url(url='scenario5.com', shortcode='08vs43')
        assert Shortcode.check_in_use('08vs43')

    def test_check_in_use_false(self):
        assert Shortcode.check_in_use('xyzxyz') is False

    def test_generate_new(self):
        assert Shortcode.check_validity(shortcode=Shortcode.generate_new())

    def test_insert_success(self):
        assert isinstance(Shortcode.insert(shortcode='000xzz'), Shortcode)

    def test_insert_invalid_shortcode_failure(self):
        with pytest.raises(Exception) as exc:  # Wide catch, scope narrowed for preventing nested Exception override
            Shortcode.insert(shortcode='090')
            assert isinstance(exc.type, InvalidShortcode.__class__)  # Sanity check

    def test_insert_shortcode_already_in_use_failure(self):
        with pytest.raises(Exception) as exc:  # Wide catch, scope narrowed for preventing nested Exception override
            Shortcode.insert(shortcode='08vs43')
            assert isinstance(exc.type, ShortcodeAlreadyInUse.__class__)  # Sanity check

    def teardown_class(self):
        remove_test_database()


@pytest.mark.usefixtures('app')
class TestStatModel:

    def setup_method(self):
        Url.insert_url(url='scenario7.com', shortcode='aqaqaq')

    def test_base_name(self):
        assert Stat.__name__ == 'Stat'

    def test_get_stats_success(self):
        stats = Stat.get_stats(shortcode='aqaqaq')
        assert 'created' in stats
        assert 'lastRedirect' in stats
        assert 'redirectCount' in stats

    def test_get_stats_shortcode_not_found_failure(self):
        with pytest.raises(Exception) as exc:  # Wide catch, scope narrowed for preventing nested Exception override
            Stat.get_stats(shortcode='0b0b0b')
            assert isinstance(exc.type, ShortcodeNotFound.__class__)  # Sanity check

    def teardown_class(self):
        remove_test_database()


@pytest.mark.usefixtures('app')
class TestRedirectModel:

    def setup_method(self):
        Url.insert_url(url='scenario8.com', shortcode='090909')

    def test_base_name(self):
        assert Redirect.__name__ == 'Redirect'

    def test_stat_redirect_is_zero(self):
        stats = Stat.get_stats(shortcode='090909')
        assert stats['redirectCount'] == 0

    def test_check_in_use_false(self):
        assert Redirect.check_in_use(shortcode='090909') is False

    def test_redirect_success(self):
        url = Redirect.redirect(shortcode='090909')
        assert url == 'scenario8.com'

    def test_stat_redirect_is_not_zero(self):
        stats = Stat.get_stats(shortcode='090909')
        assert stats['redirectCount'] == 1

    def test_check_in_use_true(self):
        assert Redirect.check_in_use(shortcode='090909')

    def test_check_in_use_failure(self):
        with pytest.raises(Exception) as exc:  # Wide catch, scope narrowed for preventing nested Exception override
            in_use = Redirect.check_in_use(shortcode='xxx')
        assert isinstance(exc.type, ShortcodeNotFound.__class__)  # Sanity check

    def teardown_class(self):
        remove_test_database()
