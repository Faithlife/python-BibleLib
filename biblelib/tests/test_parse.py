"""Test reference parsing.o """

import pytest

from biblelib import parse


@pytest.fixture
def Parser():
    return parse.Parser()


class Test_Parser(object):
    def test_Verseref(self, Parser):
        assert Parser.parse('Mark 3:4').refid == 'bible.62.3.4'

    def test_Chapterref(self, Parser):
        assert Parser.parse('Mark 3').refid == 'bible.62.3'

    def test_RangeVerseref(self, Parser):
        assert Parser.parse('Lk 4:1-9').refid == 'bible.63.4.1-63.4.9'

    def test_RangeChapterVerseref(self, Parser):
        assert Parser.parse('Lk 4:1-5:9').refid == 'bible.63.4.1-63.5.9'

    def test_RangeChapterref(self, Parser):
        assert Parser.parse('Mark 3-4').refid == 'bible.62.3-62.4'
