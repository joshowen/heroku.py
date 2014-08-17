# -*- coding: utf-8 -*-

"""
heroku.core
~~~~~~~~~~~

This module provides the base entrypoint for heroku.py.
"""

from .api import Heroku, Pgbackups, HerokuPostgres, AuthenticationError
import requests


def from_key(api_key, session=None, **kwargs):
    """Returns an authenticated Heroku instance, via API Key."""
    if not session:
        session = requests.session()
    # If I'm being passed an API key then I should use only this api key
    # if trust_env=True then Heroku will silently fallback to netrc authentication

    session.trust_env = False
    h = Heroku(session=session, **kwargs)

    # Login.
    h.authenticate(api_key)

    return h


def pg_backups(pgbackups_url, **kwargs):
    """Returns a Heroku Pgbackups client instance, via PGBACKUPS_URL."""
    pgbc = Pgbackups(**kwargs)

    # set url.
    pgbc.set_url(pgbackups_url)

    return pgbc


def postgres(api_key, heroku_postgres_host=None, **kwargs):
    """Returns a Heroku Postgres client instance, via API Key and option postgres host."""
    # Login with normal Heroku client
    h = from_key(api_key)
    if h.is_authenticated:
        hpg = HerokuPostgres(h, **kwargs)

        # set api key and url
        hpg._api_key = api_key
        hpg._set_url(heroku_postgres_host)

        return hpg
    else:
        raise AuthenticationError("Can't auth with provided api_key.")
