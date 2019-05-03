"""Parse a human-readable reference into an internal form.

Many caveats apply: see __init__.py. Only use this for things that ought
to be Bible references.

This is not a substitute for industrial strength reference parsing,
but it's sufficient for 

* batch processing where the API overhead is
too high 
* reasonably well-formed references (like internal editorial
data)

>>> from biblelib.reference import parse

This doesn't handle:

* references to single-chapter books with an elided chapter, like
  'Jude 6': use 'Jude 1:6' instead.

"""

import re


from .books import Book, get_all_booknames
from . import core


class ReferenceParserError(Exception):
#class ReferenceParserError(reference.ReferenceError):
    """Something bad happened in parsing a reference."""
    pass


class Parser(object):
    """Class for parsing human-readable Bible references into internal format. """
    # generate these to keep them in sync
    # matching bible data types
    _bibletype_regexp_template = '(?P<bibletype>{}):(?P<ref>.+)'
    _bibletype_keys = '|'.join(core.HUMAN_BIBLE_DATATYPES.keys())
    bibletype_regexp = re.compile(_bibletype_regexp_template.format(_bibletype_keys))
    # case-insensitive version
    bibletype_regexp_i = re.compile(_bibletype_regexp_template.format(_bibletype_keys), re.I)
    # matching bible book names
    _biblebook_regexp_template = '(?P<biblebook>{}) (?P<ref>.+)'
    _biblebook_keys = '|'.join(get_all_booknames())
    biblebook_regexp = re.compile(_biblebook_regexp_template.format(_biblebook_keys))
    _verseref_regexp_template = r"(?P<chapter>\d+):(?P<verse>\d+)"
    verseref_regexp = re.compile(_verseref_regexp_template)
    chapterref_regexp = re.compile(r"(?P<chapter>\d+)")
    rangechapterref_regexp = re.compile(r"(?P<chapter>\d+)[-|–](?P<endchapter>\d+)")
    rangeverseref_regexp = re.compile(r"{}[-|–](?P<endverse>\d+)".format(_verseref_regexp_template))
    rangechapterverseref_regexp = re.compile(r"{}[-|–](?P<endchapter>\d+):(?P<endverse>\d+)".format(_verseref_regexp_template))

    def __init__(self):
        pass

    def parse(self, string):
        # strip periods and other cruft
        string = string.replace('.', '').strip()
        string = re.sub(r"‐|–|—", "-", string)
        bibletype, rest = self.parse_bibletype(string)
        book, rest = self.parse_bookname(rest)
        parseargs = {'bibletype': bibletype or 'bible',
                     'book': book.index,
                     }
        if self.verseref_regexp.fullmatch(rest):
            verseref_match = self.verseref_regexp.fullmatch(rest)
            parseargs.update(chapter=verseref_match.group('chapter'),
                             verse=verseref_match.group('verse'))
            return make_verseref(**parseargs)
        elif self.rangeverseref_regexp.fullmatch(rest):
            rangeverseref_match = self.rangeverseref_regexp.fullmatch(rest)
            parseargs.update(chapter=rangeverseref_match.group('chapter'),
                             verse=rangeverseref_match.group('verse'),
                             endverse=rangeverseref_match.group('endverse'))
            return make_rangeverseref(**parseargs)
        elif self.rangechapterverseref_regexp.fullmatch(rest):
            rangechapterverseref_match = self.rangechapterverseref_regexp.fullmatch(rest)
            parseargs.update(chapter=rangechapterverseref_match.group('chapter'),
                             verse=rangechapterverseref_match.group('verse'),
                             endchapter=rangechapterverseref_match.group('endchapter'),
                             endverse=rangechapterverseref_match.group('endverse'))
            return make_rangechapterverseref(**parseargs)
        elif self.rangechapterref_regexp.fullmatch(rest):
            rangechapterref_match = self.rangechapterref_regexp.fullmatch(rest)
            parseargs.update(chapter=rangechapterref_match.group('chapter'),
                             endchapter=rangechapterref_match.group('endchapter'))
            return make_rangechapterref(**parseargs)
        elif self.chapterref_regexp.fullmatch(rest):
            chapterref_match = self.chapterref_regexp.fullmatch(rest)
            parseargs.update(chapter=chapterref_match.group('chapter'))
            return make_chapterref(**parseargs)
        else:
            raise ReferenceParserError(f"Unable to parse: {string}")
        
    def parse_bibletype(self, string, ignorecase=False):
        """Return tuple of bibletype and reference.

        First element is empty string if no bibletype.
        """
        regexp = self.bibletype_regexp_i if ignorecase else self.bibletype_regexp
        m = regexp.fullmatch(string)
        if m:
            return (core.HUMAN_BIBLE_DATATYPES.get(m.group('bibletype')),
                    m.group('ref'))
        else:
            return ("", string)

    def parse_bookname(self, string, ignorecase=False):
        """Return tuple of book object and remaining reference.

        Raise BiblerefParserError if no bookname.
        """
        # BUG: fails on space in '1 Sam 24:5'
        m = self.biblebook_regexp.fullmatch(string)
        if m:
            book, rest = (Book(m.group('biblebook')), m.group('ref'))
            return self.handle_one_chapter_book(book, rest)
        else:
            raise ReferenceParserError(f"No book name found: {string}")

    def handle_one_chapter_book(self, book, rest):
        if book.get_bookname() in ['Obad', 'Phlm', 'Jude'] and ":" not in rest:
            rest = "1:"+rest
        return book, rest

        
def make_rangechapterref(chapter, endchapter, *args, **kwargs):
    start = core.Chapterref(chapter=chapter, *args, **kwargs)
    end = core.Chapterref(chapter=endchapter, *args, **kwargs)
    return core.RangeChapterref(start, end)

def make_rangeverseref(verse, endverse, *args, **kwargs):
    start = core.Verseref(verse=verse, *args, **kwargs)
    end = core.Verseref(verse=endverse, *args, **kwargs)
    return core.RangeVerseref(start, end)

def make_rangechapterverseref(chapter, verse, endchapter, endverse, *args, **kwargs):
    start = core.Verseref(chapter=chapter, verse=verse, *args, **kwargs)
    end = core.Verseref(chapter=endchapter, verse=endverse, *args, **kwargs)
    return core.RangeVerseref(start, end)

def make_chapterref(*args, **kwargs):
    return core.Chapterref(*args, **kwargs)

def make_verseref(*args, **kwargs):
    return core.Verseref(*args, **kwargs)
