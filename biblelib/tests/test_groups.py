"""pytest tests

On the command line:
> pytest
"""

import pytest

from biblelib import groups


class TestGospels(object):
    def test_contents(self):
        gospels = groups.groupnames['Gospels']
        assert len(gospels) == 4
        assert [b.ldlsrefname for b in gospels.get_books()] == ['Mt', 'Mk', 'Lk', 'Jn']
        assert gospels.n_chapters == 89
        assert gospels.n_verses == 3779
        assert gospels.in_canon('Catholic')
        assert not(gospels.in_canon('Jewish'))
