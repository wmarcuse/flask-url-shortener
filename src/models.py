from sqlalchemy.sql import func
import string
import random
import re

from db import db as dbs
from exceptions import ShortcodeAlreadyInUse, InvalidShortcode, ShortcodeNotFound


class Url(dbs.Model):
    """
    This is the main logical entrypoint model for the url shortening
    application. As we want to prevent database pollution with multiple
    shortcodes for the same URL, the Url is the parent model for all
    underlying database models.

    For non time consuming development reasons, only One-to-One relations
    are set.
    """
    __tablename__ = 'url'
    __table_args__ = (
        dbs.UniqueConstraint(
            'url'
        ),
    )

    id = dbs.Column(dbs.Integer, primary_key=True)
    url = dbs.Column(dbs.String, nullable=False)
    shortcode = dbs.relationship('Shortcode', uselist=False, back_populates='url')

    @classmethod
    def insert_url(cls, url, shortcode=None):
        """
        This method creates a new Url record and
        returns the related shortcode. If the Url
        already exist, the existing related shortcode is returned.

        :param url: The provided URL.
        :type url: str

        :param shortcode: The provided shortcode.
        :type shortcode: str

        :return: The related shortcode.
        :rtype: str
        """
        _url = Url.query.filter_by(url=url).first()
        if _url is None:
            _shortcode = Shortcode.insert(shortcode=shortcode)
            _url = cls(url=url, shortcode=_shortcode)
        dbs.session.add(_url)
        dbs.session.commit()
        return _url.shortcode.shortcode


class Shortcode(dbs.Model):
    """
    This model is the main Shortcode model.

    For non time consuming development reasons, only One-to-One relations
    are set.
    """
    __tablename__ = 'shortcode'
    __table_args__ = (
        dbs.UniqueConstraint(
            'shortcode'
        ),
    )

    id = dbs.Column(dbs.Integer, primary_key=True)
    urlId = dbs.Column(dbs.Integer, dbs.ForeignKey('url.id'))
    url = dbs.relationship('Url', back_populates='shortcode')
    shortcode = dbs.Column(dbs.String)
    stats = dbs.relationship('Stat', uselist=False, back_populates='shortcode')

    @staticmethod
    def generate_random(length=6, chars=string.ascii_lowercase + string.digits + '_'):
        """
        This method generates a random string.

        :param length: The desired random string length.
        :type length: int

        :param chars: The provided allowed string types.
        :type chars: str|string

        :return: The random string.
        :rtype: str
        """
        return ''.join(random.choice(chars) for _ in range(length))

    @staticmethod
    def check_validity(shortcode):
        """
        This method checks if the provided shortcode matches
        the specific shortcode format, with a regex match check.

        :param shortcode: The provided shortcode.
        :type shortcode: str

        :return: The validity result.
        :rtype: bool
        """
        desired_pattern = re.compile(r'^[a-z0-9_]{6}$')
        match = desired_pattern.match(shortcode)
        if match is not None:
            return True
        else:
            return False

    @classmethod
    def check_in_use(cls, shortcode):
        """
        This method checks if the provided shortcode is already in use,
        by querying the database.

        :param shortcode: The provided shortcode.
        :type shortcode: str

        :return: The in-use status.
        :rtype: bool
        """
        _shortcode = cls.query.filter_by(shortcode=shortcode).first()
        if _shortcode is None:
            return False
        else:
            return True

    @classmethod
    def generate_new(cls):
        """
        This method generates a new shortcode, by:
            1. Generating a random string.
            2. Checking if the random string is in use.
            3. If not in use, returning the checked shortcode.

        :return: The checked new shortcode string.
        :rtype: str
        """
        while True:
            random_shortcode = cls.generate_random()
            shortcode_in_use = cls.check_in_use(shortcode=random_shortcode)
            if shortcode_in_use is False:
                checked_shortcode = random_shortcode
                break
        return checked_shortcode

    @classmethod
    def insert(cls, shortcode):
        """
        This method instantiates a new Shortcode record in the database.
        A new Stat object is also attached to the Shortcode.

        A decision tree is walked through if the client provided
        a desired shortcode to use for the url shortening.

        :param shortcode: The provided shortcode.
        :type shortcode: str

        :return: The instantiated Shortcode record
        :rtype: models.Shortcode

        .. warning::
            The Shortcode record is not committed to the database, as this
            is done on a higher-level, most likely by attaching the Shortcode
            to the Url record, and then committing to the database.
        """
        if shortcode is not None:
            shortcode_in_use = cls.check_in_use(shortcode=shortcode)
            if shortcode_in_use is False:
                shortcode_valid = cls.check_validity(shortcode=shortcode)
                if shortcode_valid is True:
                    accepted_shortcode = shortcode
                else:
                    raise InvalidShortcode
            else:
                raise ShortcodeAlreadyInUse
        else:
            accepted_shortcode = cls.generate_new()
        _stat = Stat()
        _shortcode = cls(
            shortcode=accepted_shortcode,
            stats=_stat
        )
        return _shortcode


class Stat(dbs.Model):
    """
    This model is the main Stat model.

    For non time consuming development reasons, only One-to-One relations
    are set.

    The created time is set server-side.
    """
    __tablename__ = 'stat'

    id = dbs.Column(dbs.Integer, primary_key=True)
    shortcodeId = dbs.Column(dbs.Integer, dbs.ForeignKey('shortcode.id'))
    shortcode = dbs.relationship('Shortcode', back_populates='stats', foreign_keys=[shortcodeId])
    created = dbs.Column(dbs.DateTime(timezone=True), server_default=func.strftime('%Y-%m-%d %H:%M:%f', 'now'))
    redirect = dbs.relationship('Redirect', back_populates='stat', uselist=False)

    @classmethod
    def get_stats(cls, shortcode):
        """
        This method retrieves the stats for the provided shortcode.

        :param shortcode: The provided shortcode.
        :type shortcode: str

        :return: The fetched stats for the provided shortcode.
        :rtype: dict

        .. note::
            As the Redirect child for a stat is created in a non-greedy
            way, the logic handling for a not existing Redirect is handled
            in this method.

        :raises:
            ShortcodeNotFound: When the provided shortcode does not exist.
        """
        in_use = Shortcode.check_in_use(shortcode=shortcode)
        if in_use is False:
            raise ShortcodeNotFound
        _stat = cls.query.filter(cls.shortcode.has(shortcode=shortcode)).first()
        if _stat.redirect is None:
            last_redirect = None
            redirect_count = 0
        else:
            last_redirect = _stat.redirect.lastRedirect.isoformat()
            redirect_count = _stat.redirect.redirectCount
        return {
            cls.created.name: _stat.created.isoformat(),
            Redirect.lastRedirect.name: last_redirect,
            Redirect.redirectCount.name: redirect_count
        }


class Redirect(dbs.Model):
    """
    This model is the main Redirect model.

    For non time consuming development reasons, only One-to-One relations
    are set.

        The lastRedirect time is set server-side.
    """
    __tablename__ = 'redirect'

    id = dbs.Column(dbs.Integer, primary_key=True)
    statId = dbs.Column(dbs.Integer, dbs.ForeignKey('stat.id'))
    stat = dbs.relationship('Stat', back_populates='redirect', foreign_keys=[statId])
    lastRedirect = dbs.Column(dbs.DateTime(timezone=True), server_default=func.now(), onupdate=func.strftime('%Y-%m-%d %H:%M:%f', 'now'))
    redirectCount = dbs.Column(dbs.Integer)

    @classmethod
    def check_in_use(cls, shortcode):
        """
        This method checks if a redirect record for the provided
        shortcode is already in use, by querying the database.

        :param shortcode: The provided shortcode.
        :type shortcode: str

        :return: The in-use status.
        :rtype: bool

        :raises:
            ShortcodeNotFound: When the provided shortcode does not exist.
        """
        _stat = Stat.query.filter(Stat.shortcode.has(shortcode=shortcode)).first()
        if _stat is None:
            raise ShortcodeNotFound
        else:
            _redirect = _stat.redirect
            if _redirect is None:
                return False
            else:
                return True

    @classmethod
    def redirect(cls, shortcode):
        """
        This method handles the redirect by incrementing the redirectCount
        for the Redirect record and returning the attached FQDN domain for
        the provided shortcode.

        :param shortcode: The provided shortcode.
        :type shortcode: str

        :return: The related FQDN domain.
        :rtype: str
        """
        in_use = cls.check_in_use(shortcode=shortcode)
        if in_use is True:
            _redirect = Stat.query.filter(Stat.shortcode.has(shortcode=shortcode)).first().redirect
            _redirect.redirectCount += 1

        else:
            _redirect = cls(
                stat=Stat.query.filter(Stat.shortcode.has(shortcode=shortcode)).first(),
                redirectCount=1
            )
            dbs.session.add(_redirect)
        dbs.session.commit()
        return _redirect.stat.shortcode.url.url
