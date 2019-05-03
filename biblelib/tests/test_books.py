import pytest


from biblelib import books


class TestMark(object):
    mark = books.Book('Mk')
    
    def test_names(self):
        assert self.mark.index == 62
        assert self.mark.fullname == 'Mark'
        assert self.mark.shortname == 'Mark'
        assert self.mark.ldlsrefname == 'Mk'
        assert self.mark.etdname == 'Mk'

    def test_canons(self):
        assert self.mark.in_canon('Protestant')
        assert self.mark.in_canon('Catholic')
        assert not(self.mark.in_canon('Jewish'))
        
    def test_chapters(self):
        assert self.mark.has_chapter(16)
        assert self.mark.has_chapterandverse(16, 20)
        assert self.mark.get_chapters() == \
          [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
        assert self.mark.get_finalchapter() == 16
        assert self.mark.n_verses == 678
        assert self.mark.get_finalverse(16) == 20
        assert self.mark.get_vindex(16,20) == 677
        assert self.mark.get_vindex_dtr(677) == 'bible.62.16.20'

# class TestBooknames(object)

#     def test_construction(self):
#         assert 
