# -*- coding: utf-8 -*-
"""Core classes and utilities supporting Bible references.

For parsing human readable references, see parse.py. 

>>> from biblelib.reference import core
# construct a reference from individual elements
>>> vref = core.Verseref(book=62, chapter=3, verse=4)
Verseref('bible.62.3.4')
>>> vref.userstring()
'Mk 4:2'
>>> vref.refly_url()
'https://ref.ly/logosref/Bible.Mk4.2'

# construct from a bible data type reference string
>>> vref = core.makeBiblerefFromDTR('bible.62.4.2')
>>> vref
Verseref('bible.62.4.2')

# checks for valid chapter/verse combinations (somewhat)
>>> core.Verseref(book=62, chapter=33, verse=1)
biblelib.ReferenceValidationError: Invalid chapter index: 33
>>> core.Verseref(book=62, chapter=3, verse=99)
biblelib.ReferenceValidationError: Invalid verse index: 99


See test_reference.py for detailed usage examples.

This doesn't handle:
* chapter-verse ranges (Matt 4-5:12)


TODO:
- clean up properties vs methods
- VerseRef.cmp seems broken
- add todict() methods

"""


import re
import sys
import warnings

from .books import Book
from .biblebooks import Abbreviations

# datatypes for internal-style references
# probably not complete
HUMAN_BIBLE_DATATYPES = {'Bible': 'bible',
                         'BibleNRSV': 'bible+nrsv',
                         'BibleBHS': 'bible+bhs',
                         'BibleLXX': 'bible+lxx',
                         'BibleLXX2': 'bible+lxx2',
                         'BibleESV': 'bible+esv',
                         'BibleNA27': 'bible+na27',
                         'BibleSBLGNT': 'bible+sblgnt',
                         'BibleLEB': 'bible+leb2',
                         }
MACHINE_BIBLE_DATATYPES = {v: k for k, v in HUMAN_BIBLE_DATATYPES.items()}
BIBLE_DATATYPES = HUMAN_BIBLE_DATATYPES.values()


class BiblelibError(Exception):
    """Something bad happened in biblelib."""
    pass

class ReferenceValidationError(BiblelibError):
    """Returned when validating a reference fails."""
    pass


# class hierarchy:
# GenericBibleref
# - Bibleref
#   - Bookref
#     - Chapterref
#       - Verseref
# - RangeChapterref
#   - RangeVerseref
class GenericBibleref(object):
    """Abstract class for all Bible references."""
    _cache = {}                        # symbol table for Biblerefs
    level = None
    # tuples of start/end indices to simplify subsumption checking
    _rangeindices = dict()
    # incomplete but covers the most important cases
    canon_traditions = ['Catholic', 'Jewish', 'Protestant']
    abbreviations = Abbreviations()
    
    def __init__(self, bibletype='bible'):
        """Create an instance of a Bibleref object.
        
        BIBLETYPE is a bible datatype in BIBLE_DATATYPES. 
        """
        assert self.__class__ != GenericBibleref, \
            "Bibleref is an interface, and can't be instantiated"
        assert bibletype in BIBLE_DATATYPES, "Invalid bible datatype: {}".format(bibletype)
        self.bibletype = bibletype

    def __repr__(self):
        return f"{type(self).__name__}('{self.refid}')"

    __str__ = __repr__
    
    def __len__(self): raise NotImplementedError
    def __hash__(self): return hash(self.refid)

    def _compatible_args(self, other):
        """Return a tuple of two tuples of indices. 

        For non-range references, both tuples are the same. 
        """
        assert (isinstance(self, GenericBibleref) and
                isinstance(other, GenericBibleref)), \
                f'order is only defined between Bibleref instances: {self}, {other}'
        return ((self.start.indices(), self.end.indices()),
                (other.start.indices(), other.end.indices()))
        
    def __eq__(self, other):
        selfindices, otherindices = self._compatible_args(other)
        return selfindices == otherindices
    def __lt__(self, other):
        selfindices, otherindices = self._compatible_args(other)
        return selfindices < otherindices
    def __le__(self, other):
        return self < other or self == other
        # selfindices, otherindices = self._compatible_args(self, other)
        # return selfindices < otherindices or selfindices == otherindices
        
    def datatypestring(self):
        """Return a data type string reference like 'bible.11.16.34'."""
        return self.refid
        
    def leveleq(self, other):
        """
        True iff both SELF and OTHER are Bibleref objects at the same
        level.
        """
        return isinstance(self, GenericBibleref) and \
               isinstance(other, GenericBibleref) and \
               self.level == other.level


class Bibleref(GenericBibleref):
    """Generic class for simple Bible references: don't instantiate
    this directly. Includes reference to BIBLE (datatype). """
    def __init__(self, *args, **kwargs):
        assert self.__class__ != Bibleref, \
            "Bibleref is an interface, and can't be instantiated"
        GenericBibleref.__init__(self, *args, **kwargs)
        self.params = ['bibletype']
        self.refid = self._makerefid()                    # sep. function so subclasses can override

    def _makerefid(self):
        paramlist = [getattr(self, x) for x in self.params]
        assert all(paramlist), \
               'Null element in paramlist: {}'.format(paramlist)
        return '.'.join([str(getattr(self, x)) for x in self.params])

    def indices(self):
        """Return a tuple of all available level indices. """
        return tuple([getattr(self, x) for x in self.params])

    # I'm not sure this method makes sense throughout: YAGNI?
    def sublevel_length(self, canon_tradition='Protestant'):
        """How many subunits are there?

        For non-Protestant canons, this is counting books in books.py,
        not the traditional canon organizations.
        """
        assert canon_tradition in self.canon_traditions, \
          'Invalid canon_tradition {} should be in {}'.format(canon_tradition, self.canon_traditions)
        if canon_tradition == 'Protestant': return 66
        elif canon_tradition == 'Catholic': return 87   # correct?
        elif canon_tradition == 'Jewish': return 39

    def __len__(self):
        return 1                          # by definition these are single references

    
class Bookref(Bibleref):
    """
    Reference to BIBLE and BOOK, without chapter and verse.
    """
    def __init__(self, book=0, *args, **kwargs):
        """Book is a numeric index """
        Bibleref.__init__(self, *args, **kwargs)
        self.book = int(book)
        self.level = 'book'
        self.params.append(self.level)
        self.refid = self._makerefid()
        self._rangeindices[self.level] = (self.book, self.book)
        self._bookdata = Book(self.book)
        
    def sublevel_length(self):
        """Assuming canon_tradition='Protestant' here. """
        return self._bookdata.get_finalchapter()

    def refdict(self, withbibletype=False, withbook=True, withchapter=True, withverse=True):
        """Return a dict with keys bible, book, chapter, verse.

        Book is the abbreviation. Chapter and verse are integers.  You
        can leave out book for contextual end references.
        """
        refdict = {}
        if hasattr(self, 'book') and withbook:
            refdict['book'] = self._bookdata.ldlsrefname
        if hasattr(self, 'bibletype') and withbibletype:
            refdict['bibletype'] = MACHINE_BIBLE_DATATYPES.get(self.bibletype)
        if hasattr(self, 'chapter') and withchapter:
            refdict['chapter'] = self.chapter
            if hasattr(self, 'verse') and withverse:
                refdict['verse'] = self.verse
        return refdict
        
    def userstring(self, language="en", **kwargs):
        """Return a user-readable string reference with book abbreviations.

        Specifies book as well as bible, chapter and verse unless
        withbibletype/chapter/verse is False.
        """
        refdict = self.refdict(**kwargs)
        ref = ''
        if 'bibletype' in refdict:
            ref += "{bibletype}:".format(**refdict)
        if 'book' in refdict:
            book = self.abbreviations.abbreviation_for_en(refdict['book'], language=language)
            ref += "{0}".format(book)
        if 'chapter' in refdict:
            ref += " {chapter}".format(**refdict)
            if 'verse' in refdict:
                ref += ":{verse}".format(**refdict)
        return ref 

    def _make_uri(self):
        "Common code for making URI strings. "
        refdict = self.refdict(withbibletype=True)
        ref = "{bibletype}.{book}".format(**refdict)
        if 'chapter' in refdict:
            ref += str(refdict.get('chapter'))
            if 'verse' in refdict:
                ref += '.{}'.format(refdict.get('verse'))
        return ref

    def refly_url(self):
        """Return a ref.ly URL for self. """
        return "https://ref.ly/logosref/{}".format(self._make_uri())

    def logosref_uri(self):
        """Return a string for self under the Logos URI Protocol.

        See https://wiki.lrscorp.net/logosref_Protocol. """
        return "logosref:{}".format(self._make_uri())

    def get_chapters(self):
        return self._bookdata.get_chapters()
        
    def has_chapter(self, index):
        return self._bookdata.has_chapter(index)

    
class Chapterref(Bookref):
    """A reference to Book and Chapter, without verse. """
    def __init__(self, chapter=0, *args, **kwargs):
        Bookref.__init__(self, *args, **kwargs)
        self.chapter = int(chapter)
        self.level = 'chapter'
        self.params.append(self.level)
        self.refid = self._makerefid()
        self._rangeindices[self.level] = (self.chapter, self.chapter)
        if not self._bookdata.has_chapter(self.chapter):
            raise ReferenceValidationError("Invalid chapter index: %d" % self.chapter)
        # for consistency with ranges
        self.start = self
        self.end = self
        
    def _subcheck(self, other):
        Bookref._subcheck(self, other)
        assert self.book == other.book, \
               "Subtraction undefined for different books: %s and %s" % (self, other)

    def sublevel_length(self):
        return self._bookdata.get_finalverse(self.chapter)

    def subsumes(self, other):
        """
        True if OTHER's level is at or below SELF's, and OTHER has the
        same indexes as each of SELF's. This hierarchical inclusion is
        perhaps subtly different from range subsumption.
        """
        # other's level is below if it's not in self's params
        if self.level in other.params:
            if (isinstance(self, Chapterref) and
                isinstance(other, RangeVerseref)):
                # other has no chapter attrs (start and end might differ)
                return (self.book == other.book and
                        self.chapter == other.start.chapter and
                        self.chapter == other.end.chapter)
            else:
                return all(lambda p: getattr(other, p) == getattr(self, p),
                             self.params)
    def get_finalverse(self):
        return self._bookdata.get_finalverse(self.chapter)
    
    # hack! assumes the first verse is 1, which isn't always true
    def toVerseref(self):
        "Return a Verseref to verse 1 in the chapter"
        return Verseref(book=self.book, chapter=self.chapter, verse=1)


class Verseref(Chapterref):
    """A simple reference to BOOK, CHAPTER, and VERSE.

    Assumes chapters whose first verse has index=1.
    """
    def __init__(self, verse=0, **kwargs):
        Chapterref.__init__(self, **kwargs)
        self.verse = verse
        self.level = 'verse'
        self.verseindex = self._bookdata.get_vindex(self.chapter, self.verse)
        self.params.append(self.level)
        self._makerefid()
        self._rangeindices[self.level] = (self.verse, self.verse)
        if not self._bookdata.has_chapterandverse(self.chapter, self.verse):
            errmsg = "Invalid verse index {} for chapter={}".format(self.verse, self.chapter)
            raise ReferenceValidationError(errmsg)
        # for consistency with RangeVerseref
        self.start = self
        self.end = self

    # override of Bibleref method to handle Ps titles
    def _makerefid(self):
        paramvals = [str(getattr(self, x)) for x in self.params]
        # tinker if the verse value is '0'
        if paramvals[-1] == '0':
            paramvals[-1] = 'title'
        self.refid = '.'.join(paramvals)
        assert all([getattr(self, x) for x in self.params]), \
               'Null element in %s' % self.refid
        return self.refid

    # this signals a problem with my class model :-/
    def sublevel_length(self):
        raise NotImplementedError("Verserefs don't have sub levels")

    # this may seem silly, but enables easier intersection checking for RangeVerseref
    def enumerateverses(self):
        """Return a list of self, a degenerate case of enumeration. """
        return [self]

    def intersection(self, other, sort=False):
        """Return the common verses between SELF and OTHER.

        Vacuous case for consistency: if OTHER == SELF, return
        list(SELF), else ().
        """
        assert (isinstance(other, GenericBibleref) and other.level == 'verse'), \
                "intersection not defined for %s" % other
        if self == other:
            return [self]
        elif isinstance(other, RangeVerseref) and self in other.EnumerateVerses():
             return [self]
        else:
            return []
        

# # added coverage for this, but this really ought to be integrated further with
# # RangeChapterref
# class RangeBookref(GenericBibleref):
#     """
#     A range format is a composite of start and end Bookref objects.

#     Some functionality isn't provided here
#     """
#     def __init__(self, start, end, force=False, validate=False):
#         """With FORCE, make it a range even if it isn't."""
#         GenericBibleref.__init__(self)
#         assert (isinstance(start, Bibleref) and isinstance(end, Bibleref)), \
#                "start %s and end %s must both be Bibleref objects" % (start, end)
#         (self.start, self.end) = (start, end)
#         assert (start.bibletype == end.bibletype), \
#                "start %s and end %s must be in the same bible" % (start, end)
#         self.bibletype = self.start.bibletype
#         self.book = self.start.book
#         assert start.leveleq(end), \
#                "start %s and end %s must be at the same level" % (start, end)
#         self.level = self.start.level
#         self.params = self.start.params
#         assert self.start.index <= self.end.index, \
#                "start %s must precede end %s" % (start, end)
#         self._rangeindices['book'] = (getattr(self.start, 'book'),
#                                          getattr(self.end, 'book'))
#         # like the Lbx parser, the end part includes book, chapter,
#         # and verse, even if redundant with the start
#         shortid = self.end.id[len(self.end.bibletype)+1:]
#         self.id = "%s-%s" % (self.start.id, shortid)

#     def userstring(self, withbibletype=False):
#         """Return a string reference in traditional format using the
#         LDLS book abbreviations, like '1 Ki 16:34'.

#         If WITHBIBLETYPE is True, include the bible datatype.
#         """
#         # return Unicode with an emdash
#         return u"{}–{}".format(self.start.userstring(withbibletype=withbibletype),
#                               self.end.userstring())

#     def logos_bible_url(self, domain='http://bible.logos.com',
#                         passage='passage', version='NIV'):
#         """
#         Return a URL for this reference at bible.logos.com.
#         """
#         return "%s/%s/%s/%s" % (domain, passage, version,
#                                 self.userstring().replace(':', '.'))
        
#     def Validate(self):
#         """Raise a BiblerefValidationError if SELF isn't a well-formed range
#         (vacuous ranges are allowed). Checks the component start and
#         end as well."""
#         self.start.Validate()
#         self.end.Validate()
#         return True
    
#     def indices(self):
#         """Return a start/end tuple of tuples of indices for start and
#         end."""
#         return (self.start.indices, self.end.indices)

#     def GetBookname(self, nametype='userstringname'):
#         return self.start.GetBookname(nametype=nametype)

#     def _levelsubsumes(self, other, level):
#         """
#         True iff SELF's indices at LEVEL are the same as OTHER's or
#         subsume it.
#         """
#         (selfir, otherir) = (self._rangeindices, other._rangeindices)
#         if level in selfir and level in otherir: 
#             return (otherir.get(level)[0] >= selfir.get(level)[0] and
#                     otherir.get(level)[1] <= selfir.get(level)[1])
#         elif hasattr(self, level) and hasattr(other, level):
#             # both have this level: values must be the same
#             return getattr(self, level) == getattr(other, level)

#     def Subsumes(self, other):
#         """True if OTHER's level is at or below SELF's, and OTHER's
#         range is within SELF's (inclusive, including the case of a
#         single verse reference). This also means any range subsumes
#         itself. May give bogus results for bogus ranges."""
#         if self.level in other.params:
#             # all common levels must have the same values or subsuming ones
#             return all(lambda p: self._levelsubsumes(other, p), 
#                          self.params)

#     # be nice to have intersection, but that's hard to do right for chapters
#     # def intersection(self, other):
   
#     # ToDo:
#     # enumeration (more generally) and indexing and iteration

#     def __len__(self):
#         """The number of items at self.level between start and end,
#         inclusive. So 1:1-1:2 is size 2, not 1, and the smallest range
#         length is 1."""
#         return (self.end - self.start) + 1

#     # "rich" comparison is only partiall defined for RangeChapterref and subs
#     # i'm not sure what the semantics of lt/gt would be in general:
#     # Subsumes and Overlaps are clearer
#     # does this fully replace __cmp__() ?
#     def __eq__(self, other):
#         return (self.__class__ == other.__class__ and
#                 self.start == other.start and
#                 self.end == other.end)

#     def __ne__(self, other):
#         return ((self.__class__ != other.__class__) or
#                 (self.start != other.start) or
#                 (self.end != other.end))



class RangeChapterref(GenericBibleref):
    """Range of chapters, e.g. Mark 1-4.

    Both start and end must be at the same level. Cross-bible and
    cross-book ranges are not allowed.
    """
    def __init__(self, start, end, force=False, validate=False):
        """With FORCE, make it a range even if it isn't."""
        GenericBibleref.__init__(self)
        assert (isinstance(start, Chapterref) and isinstance(end, Chapterref)), \
               "start %s and end %s must both be Chapterref objects" % (start, end)
        assert ((start.bibletype == end.bibletype) and (start.book == end.book)), \
               "start %s and end %s must be in the same bible and book" % (start, end)
        assert start.leveleq(end), \
               "start %s and end %s must be at the same level" % (start, end)
        (self.start, self.end) = (start, end)
        self.bibletype = self.start.bibletype
        self.book = self.start.book
        self._bookdata = self.start._bookdata
        self.level = self.start.level
        self.params = self.start.params
        assert self.start.chapter <= self.end.chapter, \
               "start %s must precede end %s" % (start, end)
        self._rangeindices['chapter'] = (getattr(self.start, 'chapter'),
                                         getattr(self.end, 'chapter'))
        # end part includes book, chapter, and verse
        shortrefid = self.end.refid[len(self.end.bibletype)+1:]
        self.refid = "%s-%s" % (self.start.refid, shortrefid)

    def userstring(self, language="en", withbibletype=False):
        """Return a string reference in traditional format using the
        LDLS book abbreviations, like '1 Ki 16:34'. This is how
        reference attributes in data elements are formatted. If
        WITHBIBLETYPE is True, include the bible datatype."""
        start_refdict = self.start.refdict()
        ref = "{0} {1}".format(self.abbreviations.abbreviation_for_en(start_refdict['book'], language=language),
                               start_refdict['chapter'])
        if self.end.chapter != self.start.chapter:
            ref += u"–{}".format(self.end.chapter)
            if self.level == 'verse':
                ref += ":{}".format(self.end.verse)
        elif self.level == 'verse':
            ref += u"–{}".format(self.end.verse)
        return ref 

    def refly_url(self):
        """Return a ref.ly URL for self. """
        return "https://ref.ly/logosref/{}-{}".format(self.start._make_uri(),
                                                      self.end.chapter)

    def logosref_uri(self):
        """Return a string for self under the Logos URI Protocol.

        See https://wiki.lrscorp.net/logosref_Protocol. """
        return "logosref:{}-{}".format(self.start._make_uri(), self.end.chapter)

    def indices(self):
        """Return a start/end tuple of tuples of indices for start and
        end."""
        return (self.start.indices(), self.end.indices())

    def _levelsubsumes(self, other, level):
        """
        True iff SELF's indices at LEVEL are the same as OTHER's or
        subsume it.
        """
        (selfir, otherir) = (self._rangeindices, other._rangeindices)
        if level in selfir and level in otherir: 
            return (otherir.get(level)[0] >= selfir.get(level)[0] and
                    otherir.get(level)[1] <= selfir.get(level)[1])
        elif hasattr(self, level) and hasattr(other, level):
            # both have this level: values must be the same
            return getattr(self, level) == getattr(other, level)

    def sublevel_length(self):
        # """
        # Return the number of verses in all the component chapters
        # """
        # total = 0
        # bbook = Book(self.book)
        # for chap in range(len(self)):
        #     index = chap + self.start.chapter
        #     total += bbook.GetFinalVerse(index)
        # return total
        raise NotImplementedError("RangeChapterrefs don't have sub levels")

    def subsumes(self, other):
        # """True if OTHER's level is at or below SELF's, and OTHER's
        # range is within SELF's (inclusive, including the case of a
        # single verse reference). This also means any range subsumes
        # itself. May give bogus results for bogus ranges."""
        # if self.level in other.params:
        #     # all common levels must have the same values or subsuming ones
        #     return all(lambda p: self._levelsubsumes(other, p), 
        #                  self.params)
        raise NotImplementedError

    # be nice to have intersection, but that's hard to do right for chapters
    # def intersection(self, other):
   
    # def rangeweight(self, other):
    #     """
    #     Given that SELF subsumes OTHER (a GenericBibleref instance at
    #     the same level), return a weight. Default is
    #     len(other)/len(self).
    #     """
    #     return len(other)/float(len(self))

    # def rangeedge(self, other):
    #     """A little more weight if first or last in a reference"""
    #     return self.rangeweight(other) * 2
    
    # ToDo:
    # enumeration (more generally) and indexing and iteration

    def __len__(self):
        """The number of items at self.level between start and end,
        inclusive. So 3-4 has length 2, not 1, and the smallest range
        length is 1."""
        return (int(self.end.chapter) - int(self.start.chapter)) + 1

    # "rich" comparison is only partiall defined for RangeChapterref and subs
    # i'm not sure what the semantics of lt/gt would be in general:
    # Subsumes and Overlaps are clearer
    # does this fully replace __cmp__() ?
    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.start == other.start and
                self.end == other.end)

    def __ne__(self, other):
        return not(self.eq(other))



class RangeVerseref(RangeChapterref):
    """
    A composite of start and end Verseref objects.
    """
    def __init__(self, start, end, **kwargs):
        """With FORCE, make it a range even if it isn't."""
        RangeChapterref.__init__(self, start=start, end=end, **kwargs)
        assert self.start.verseindex <= self.end.verseindex, \
               "start %s must precede end %s" % (start, end)
        # not sure how these are used, so could be wrong
        self._rangeindices['verse'] = (self.start.verseindex, self.end.verseindex)
        
    # potentially inefficient use of VerserefFromIndex
    def enumerateverses(self):
        """Return an ordered list of Simpleref instances for
        the individual verses in SELF."""
        verses = []
        cursor = self.start.verseindex
        try:
            while (cursor <= self.end.verseindex):
                verses.append(VerserefFromIndex(book=self.book, index=cursor))
                cursor += 1
        except:
            raise ValueError("EnumerateVerses failed on %s" % self)
        return verses

    # this signals a problem with my class model :-/
    def sublevel_length(self):
        raise NotImplementedError("RangeVerserefs don't have sub levels")

    def userstring(self, language="en", withbibletype=False):
        """Return a string reference in traditional format using the
        LDLS book abbreviations, like '1 Ki 16:33-34'. This is how
        reference attributes in data elements are formatted."""
        userstring = "{0}–{1}".format(self.start.userstring(language), self.end.verse)
        if self.start.chapter != self.end.chapter:
            userstring = "{0}–{1}:{2}".format(self.start.userstring(language), self.end.chapter, self.end.verse)
        return userstring

    def refly_url(self):
        """Return a ref.ly URL for self. """
        refly_url =  "https://ref.ly/logosref/{}-{}".format(self.start._make_uri(),
                                                                self.end.verse)
        if self.start.chapter != self.end.chapter:
            refly_url = "https://ref.ly/logosref/{}-{}:{}".format(self.start._make_uri(),
                                                                  self.end.chapter, self.end.verse)
        return refly_url

    def logosref_uri(self):
        """Return a string for self under the Logos URI Protocol.

        See https://wiki.lrscorp.net/logosref_Protocol. """
        return "logosref:{}-{}".format(self.start._make_uri(), self.end.verse)

    def intersection(self, other, sort=False):
        """Return the common verses between SELF and OTHER.
        
        The order is undefined unless SORT=True.
        """
        assert (isinstance(other, GenericBibleref) and other.level == 'verse'), \
                "intersection not defined for %s" % other
        isection = list(set(self.EnumerateVerses()).intersection(set(other.EnumerateVerses())))
        if sort:
            isection.sort()
        return isection

    def __len__(self):
        """The number of items at self.level between start and end,
        inclusive. So 3-4 has length 2, not 1, and the smallest range
        length is 1."""
        return (self.end.verseindex - self.start.verseindex) + 1


# ##### Utilities for constructing Bibleref objects



# # verse=0 is now valid for Psalm titles
# # ToDo: something useful with errors
def makeBibleref(bibletype='bible', book=0, chapter=0, verse=-1, errors='strict'):
    """
    Factory method that builds a Book/Chapter/Verseref, and also
    registers its id in a symbol table so an existing object is
    returned rather than recreated.
    """
    if isinstance(verse, str):
        verse = re.sub('(?<=[0-9])[a-z]+$', '', str(verse))  #KLUDGE!!!!!!!
    params = [bibletype]
    # bad hack
    if verse == 'title':
        verse = 0
    (book, chapter, verse) = map(int, [book, chapter, verse])
    if book:
        params.append(book)
        if chapter:
            params.append(chapter)
            if verse > -1:
                params.append(verse)
    refid = '.'.join([str(x) for x in params])
    if refid in GenericBibleref._cache:
        return GenericBibleref._cache.get(refid)
    else:
        if chapter:
            if verse > -1:
                obj = Verseref(bibletype=bibletype, book=book, chapter=chapter, verse=verse)
            else:
                obj = Chapterref(bibletype=bibletype, book=book, chapter=chapter)
        else:
            obj = Bookref(bibletype=bibletype, book=book)
        GenericBibleref._cache[obj.refid] = obj
        return obj

    
# # ToDo: something useful with errors
def makeRangeref(start=None, end=None, bibletype='bible', errors='strict'):
    # fragile shortcut!
    shortrefid = end.refid[len(end.bibletype)+1:]
    refid = "%s-%s" % (start.refid, shortrefid)
    if refid in GenericBibleref._cache:
        return GenericBibleref._cache.get(refid)
    else:
        # gotcha: you may be surprised that isinstance(Verseref, Chapterref) ==
        # True. So always test Verseiness before Chapteriness.
        if isinstance(start, Verseref) and isinstance(end, Verseref):
            obj = RangeVerseref(start=start, end=end)
        # mixed verse and chapter: convert the chapter to verseref as well
        elif isinstance(start, Verseref) and isinstance(end, Chapterref):
            # handles bible.1.1.12-1.23: convert the end to a verse ref as well
            obj = RangeVerseref(start=start, end=end.toVerseref())
        elif isinstance(end, Verseref) and isinstance(start, Chapterref):
            # handles bible.1.12-1.13.3: convert the start to a verse ref as well
            obj = RangeVerseref(start=start.toVerseref(), end=end)
        elif isinstance(start, Chapterref) and isinstance(end, Chapterref):
            obj = RangeChapterref(start=start, end=end)
        elif isinstance(start, Bookref) and isinstance(end, Bookref):
            obj = RangeBookref(start=start, end=end)
        # not handling mixed type with book
        else:
            raise ValueError('Invalid input to makeRangeref: {}, {}'.format(start, end))
        GenericBibleref._cache[obj.refid] = obj
        return obj
            
            
def VerserefFromIndex(bibletype='bible', book=0, index=0):
    """
    Given BOOK and a zero-based INDEX into its verses, return the
    corresponding Verseref object. Minimal range checking on INDEX.
    """
    book = Book(int(book))
    chapter, verse = book.get_vindex_chapter_verse(index)
    return Verseref(bibletype=bibletype, book=book, chapter=chapter, verse=verse)


def makeBiblerefFromDTR(ref, errors='strict'):
    """Return a Bibleref object for a data type reference like u'bible.64.3.16'.

    If errors=='filter', return None: use this for bad input. If
    errors=='ignore', just return the (possibly invalid) input
    unconverted.
    """
    def fullmatch(regexp, string):
        # fullmatch is Python3 only
        if sys.version_info.major < 3:
            match = regexp.match(string)
            if match and match.start() == 0 and match.end() == len(string):
                return match
        else:
            return regexp.fullmatch(string)
        
    assert errors in ['strict', 'ignore', 'filter'], 'Invalid errors value: {}'.errors
    range_regexp = re.compile(r"(?P<start>.+)[-|–](?P<end>.+)")
    try:
        if fullmatch(range_regexp, ref):
            range_match = fullmatch(range_regexp, ref)
            (start, end) = range_match.groups()
            (bible, startref) = start.split('.', 1)
            end = "%s.%s" % (bible, end)
            startref = makeBibleref(**dict(zip(['bibletype', 'book', 'chapter', 'verse'],
                                                start.split('.')),
                                                errors=errors))
            endref = makeBibleref(**dict(zip(['bibletype', 'book', 'chapter', 'verse'],
                                                end.split('.')),
                                                errors=errors))
            return makeRangeref(start=startref, end=endref, errors=errors)
        else:
            ref = re.sub(r'\.title$', '.0', ref)
            return makeBibleref(**dict(zip(['bibletype', 'book', 'chapter', 'verse'],
                                            ref.split('.')),
                                            errors=errors))
    except Exception as e:
        if errors=='strict':
            raise e
        if errors=='filter':
            warnings.warn('{} calling makeBiblerefFromDTR:\n{}\nReturning None'.format(type(e).__name__, e, ref))
            return None
        elif errors=='ignore':
            warnings.warn('{} calling makeBiblerefFromDTR:\n{}\nIgnoring error and returning {} as string'.format(type(e).__name__, e, ref))
            return ref


# # convenience function so i can apply makeBiblerefFromDTR to lots of data and return bad data unchanged
# def UserrefFromDTR(ref):
#     """Return a user-readable reference, or the input string if not processable"""
#     result = makeBiblerefFromDTR(ref, errors='ignore')
#     if isinstance(result, GenericBibleref):
#         return result.userstring()
#     else:
#         return ref



# # wish i could just do this in a lambda
# def protect_plus(string):
#     if '+' in string: return string.replace('+', '\+')
#     else: return string

# # just testing bible and book
# MACHINEREF_REGEXP = re.compile('(?P<bible>%s)\.(?P<book>\d+)' %
#                                '|'.join(map(protect_plus,
#                                             MACHINE_BIBLE_DATATYPES.keys())))


# def humanrefFromLdlsref(string):
#     """If STRING can be 'parsed' as an Ldlsref (bible.3.4.5), return
#     the human readable reference: otherwise return STRING
#     unchanged. Does no validation.
#     """
#     m = MACHINEREF_REGEXP.match(string)
#     if m:
#         try:
#             br = makeBiblerefFromLdlsref(string)
#             return br.userstring(withbibletype=True)
#         except LdlsrefError:
#             return string
#     else:
#         return string

# global _LDLS, _refcache
# _LDLS = None
# _refcache = {}

# def Biblia2Bibleref(result):
#     """
#     Given a valid result from calling Biblia's parse service, return a
#     list of bibleref objects (may be empty).
#     """
#     biblerefs = []
#     for r in result:
#         parts = r.get('parts')
#         bb = Book(parts['book'])
#         if not bb:
#             raise ValueError('Biblia2Bibleref: failed on %s' % r.get('passage'))
#         parts.update({'book': int(bb.refid)})
#         # filter out extraneous keys
#         startparts = dict([(k, v) for k, v in parts.items()
#                            if k in ['book', 'chapter', 'verse']])
#         startref = makeBibleref(**startparts)
#         if parts.get('endVerse'):
#             # not handling cross-book ranges
#             endparts = {
#                 'book': parts['book'],
#                 'chapter': parts.get('endChapter') or parts.get('chapter'),
#                 'verse': parts.get('endVerse'),
#                 }
#             endref = makeBibleref(**endparts)
#             biblerefs.append(makeRangeref(start=startref, end=endref))
#         else:
#             biblerefs.append(startref)
#     return biblerefs


# def GetBibliaLink(reference='', bible='nrsv'):
#     """
#     Pass in reference from RenderBibleReference using English/full=False
#     """
#     ref = re.sub(r' *', r'', reference)
#     ref = re.sub(r':', r'.', ref)
#     return 'http://biblia.com/bible/%s/%s' % (bible, ref)


# def LdlsParseBibleref(string, bibletype='bible', lang='en'):
#     """
#     Given a string like 'Jn 3:16', uses Libronix to return a Lbx-style
#     reference like u'bible.64.3.16', or u'' if none can be
#     parsed. Uses English book names and abbreviations unless a
#     different LANG is supplied. Does not validate verse or chapter
#     indices to ensure they're valid, and makes guesses about
#     over-abbreviated book names like 'J'. If prefixed with a Bible
#     datatype like 'Bible:', 'BibleBHS:' or 'BibleLXX:', maps that to
#     the datatype: otherwise assumes 'bible'.
#     """
#     raise NotImplementedError('LdlsParseBibleref is deprecated: use logos_pyutil.clients.ReferenceUtility')
#     # global _LDLS
#     # # only start it once
#     # if not _LDLS:
#     #     raise SystemError, \
#     #         'This COM interface has been deprecated'
#     #     _LDLS = LbxApplication()
#     # cachekey = (string, bibletype, lang)
#     # if cachekey in _refcache:
#     #     # if it's in the cache, return it directly
#     #     return _refcache.get(cachekey)
#     # else:
#     #     hbr = isHumanBibleref(string)
#     #     if hbr:
#     #         (bibletype, string) = hbr
#     #     ref = _LDLS.Application.DataTypeManager.Parse(datatype, string, lang).reference
#     #     # print "%s + %s -> %s" % (bibletype, string, ref)
#     #     if not ref:
#     #         raise BiblerefParserError, "LDLS parser returned empty string"
#     #     else:
#     #         _refcache[cachekey] = makeBiblerefFromLdlsref(ref)
#     #         return _refcache[cachekey]


# # this doesn't handle alternate bible datatypes yet
# def LdlsMultiParseBibleref(string, lang='en'):
#     """
#     Given a string containing multiple Bible references like 'Jn
#     3:16', uses Libronix to return a list of Lbx-style reference like
#     u'bible.64.3.16', or the empty list if none can be parsed. Same
#     caveats as LdlsParseBibleref. There doesn't seem to be any
#     tolerance of non-reference stuff in the string, so keep it
#     clean.
#     Issues:
#     - Returns Chapterrefs for single-chapter books like 'Let Jer 11',
#     which probably isn't what you want.
#     - Ez is Ezra, not Ezekiel, which may surprise you
#     - () and [] cause misbehavior
#     - context is carried over: if you have references that change book
#       context inside a (), and that fails (it will), then you'll get
#       completions of underspecified references that you don't expect
#     """
#     global _LDLS
#     # only start it once
#     if not _LDLS:
#         raise SystemError('This COM interface has been deprecated')
#         _LDLS = LbxApplication()
#     biblerefs = []
#     cleanstr = string.strip(' ;,\r')
#     refs = list(_LDLS.Application.DataTypeManager.MultiParse("bible", string, lang).references)
#     if refs:
#         return [makeBiblerefFromLdlsref(x) for x in refs]
#     else:
#         return []


# ##### matching logic and weights

# def matchweight(self, other,
#                 functions = {'rangestart': RangeChapterref.rangeedge,
#                              'rangeend': RangeChapterref.rangeedge,
#                              'range': RangeChapterref.rangeweight,
#                              'verseinchapter': Chapterref.verseweight,
#                              'rangeverseinchapter': RangeChapterref.verseweight,
#                              }):
#     """
#     Return a weight for the match between SELF and OTHER. Identity =
#     1, and no match = 0, otherwise the weight is derived by the value
#     in FUNCTIONS for the match key as follows:
    
#     'rangestart', 'rangeend' (self.rangeedge, defaults to 2 * rangeweight)
#     'range' (range subsuming same-level ref, either single or range) = self.rangeweight(other),
#         defaults to len(other)/len(self)
#     '[range]verseinchapter' ([Range]Chapterref subsuming [Range]Verseref) = self.verseweight(other),
#         defaults to len(other)/self.sublevel_length()
    
#     You can supply your own dictionaries of FUNCTIONS, but the keys
#     listed above are required.
#     """
#     if self == other:
#         return 1
#     elif self.Subsumes(other):
#         try:
#             if isinstance(self, RangeChapterref):
#                 if self.leveleq(other):
#                     # default if nothing better fits
#                     fn = functions.get('range')
#                     if isinstance(other, Chapterref):
#                         if self.start.indices == other.indices:
#                             fn = functions.get('rangestart')
#                         if self.end.indices == other.indices:
#                             fn = functions.get('rangeend')
#                 else:                       # other must be Verseref or RangeVerseref
#                     fn = functions.get('rangeverseinchapter')
#             elif (isinstance(self, Chapterref) and isinstance(other, Verseref)):
#                 fn = functions.get('verseinchapter')
#             return fn(self, other)
#         except:
#             print("matchweight failed on %s and %s" % (self, other))
#     else:                               # 0 if nothing else fits
#         return 0
    
