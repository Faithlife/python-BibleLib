"""Test core reference functionality. """

import pytest


from biblelib import core


class TestBookref(object):

    def test_attrs(self):
        mark = core.Bookref(62)
        assert len(mark) == 1
        assert mark.datatypestring() == 'bible.62'
        assert mark.has_chapter(4)
        assert mark.indices() == ('bible', 62)
        assert mark.level == 'book'
        assert mark.leveleq(core.Bookref(63))
        assert mark.logosref_uri() == 'logosref:Bible.Mk'
        assert mark.refid == 'bible.62'
        assert mark.params == ['bibletype', 'book']
        assert mark.refdict(withbibletype=True) == \
          {'bibletype': 'Bible', 'book': 'Mk'}
        assert mark.refly_url() == 'https://ref.ly/logosref/Bible.Mk'
        assert mark.sublevel_length() == 16
        assert mark.userstring(withbibletype=True) == 'Bible:Mk'
        assert str(mark) == "Bookref('bible.62')"

    def test_order(self):
        matt = core.Bookref(61)
        mark = core.Bookref(62)
        assert matt < mark
        assert matt <= mark
        assert mark > matt
        assert mark == mark
        assert matt != mark
    
class Test_Chapterref(object):
    mark3 = core.Chapterref(book=62, chapter=3)
    mark4 = core.Chapterref(book=62, chapter=4)

    def test_Chapterref(self):
        assert self.mark4.params == ['bibletype', 'book', 'chapter']
        assert self.mark4.refid == 'bible.62.4'
        #assert self.mark4._rangeindices == {'chapter': (4, 4), 'book': (62, 62)}
        assert self.mark4.sublevel_length() == 41
        assert self.mark4.userstring(withbibletype=True) == 'Bible:Mk 4'
        assert self.mark4.refly_url() == 'https://ref.ly/logosref/Bible.Mk4'
        assert self.mark4.logosref_uri() == 'logosref:Bible.Mk4'
        assert self.mark4.get_finalverse() == 41

    def test_order(self):
        assert self.mark3 < self.mark4
        assert self.mark3 <= self.mark3
        assert self.mark4 > self.mark3
        assert self.mark3 == self.mark3
        assert self.mark3 != self.mark4
        

class Test_Verseref(object):
    mark41 = core.Verseref(book=62, chapter=4, verse=1)
    mark49 = core.Verseref(book=62, chapter=4, verse=9)

    def test_Verseref(self):
        assert self.mark49.params == ['bibletype', 'book', 'chapter', 'verse']
        assert self.mark49.refid == 'bible.62.4.9'
        assert self.mark49.userstring(withbibletype=True) == 'Bible:Mk 4:9'
        assert self.mark49.refly_url() == 'https://ref.ly/logosref/Bible.Mk4.9'
        assert self.mark49.logosref_uri() == 'logosref:Bible.Mk4.9'

    def test_refdict(self):
        refdict = self.mark49.refdict(withbibletype=True)
        assert refdict.get('bibletype') == 'Bible'
        assert refdict.get('book') == 'Mk'
        assert refdict.get('chapter') == 4
        assert refdict.get('verse') == 9

    # def test_intersection(self):
    #     #assert not(mark41.intersection(mark49))
    #     pass


class Test_RangeVerseref(object):
    mark41 = core.Verseref(book=62, chapter=4, verse=1)
    mark49 = core.Verseref(book=62, chapter=4, verse=9)
    mark41_49 = core.RangeVerseref(mark41, mark49)

    def test_Verseref(self):
        assert self.mark41_49.params == ['bibletype', 'book', 'chapter', 'verse']
        assert self.mark41_49.refid == 'bible.62.4.1-62.4.9'
        assert self.mark41_49.userstring(withbibletype=True) == 'Bible:Mk 4:1–9'
        assert self.mark41_49.refly_url() == 'https://ref.ly/logosref/Bible.Mk4.1-9'
        assert self.mark41_49.logosref_uri() == 'logosref:Bible.Mk4.1-9'
        assert self.mark41_49.indices() == (('bible', 62, 4, 1), ('bible', 62, 4, 9))


class Test_makeBibleref(object):
    def test_makeBibleref(self):
        assert core.makeBibleref(book=62).refid == 'bible.62'
        assert core.makeBibleref(book=62, chapter=4).refid == 'bible.62.4'
        assert core.makeBibleref(book=62, chapter=4, verse=9).refid == 'bible.62.4.9'

        
class Test_makeRangeref(object):
    mark3 = core.Chapterref(book=62, chapter=3)
    mark4 = core.Chapterref(book=62, chapter=4)
    mark41 = core.Verseref(book=62, chapter=4, verse=1)
    mark49 = core.Verseref(book=62, chapter=4, verse=9)
    
    def test_makeRangeref(self):
        assert core.makeRangeref(self.mark3, self.mark4).refid == 'bible.62.3-62.4'
        assert core.makeRangeref(self.mark41, self.mark49).refid == 'bible.62.4.1-62.4.9'

# need tests for makeBiblerefFromDTR
