"""
Reader for and interface to Logos in-house pericope sets

>>> ps = pericope.PericopeSet()
# read the data
# currently some issue here with the ParagraphPericopes, which include deuterocanon
# PericopesForSearch.xml works though
>>> ps.read(file='/Users/sboisen/git/CI/ShipPericopes/legacy/ParagraphPericopesForSearch.xml')
>>> ps.start
Pericope('Ge 1:1-5', 'Paragraph 1')
>>> ps.start.next
Pericope('Ge 1:6-8', 'Paragraph 2')
# find the pericopes for a reference
>>> from libronix import bibleref
>>> bref = bibleref.makeBiblerefFromDTR('bible.1.50.20-1.50.22')
>>> ps.find(bref)
[Pericope('Ge 50:15-21', 'Paragraph 284'), Pericope('Ge 50:22-23', 'Paragraph 285')]
# write out as treemap data
>>> ps.write_as_treemap(outstr=open('/Users/sboisen/tmp/pericope_treemap.txt', 'w'))
# write out as UMd HCIL treemap data
>>> ps.write_as_umd_treemap(outstr=open('/Users/sboisen/tmp/pericope_treemap.tm3', 'w'))

This whole thing needs a rewrite
- use iterables
- make it more general
"""

import os
import json

from lxml import etree
from pathlib import Path

# old-school
# should move to new style
from libronix import bibleref
# new-style
from logos_pyutil.clients.ReferenceUtility import ReferenceUtility as ru

from libronix.biblebooks import bible
from libronix.visualization import Treemap

_REFERENCE_CACHE = {}


class Pericope(object):
    """Models an individual pericope.
    """
    def __init__(self, ref, title):
        """Create a Pericope instance given
        - ref: a Libronix-style range like bible.1.1.1-1.1.13
        - title: a string
        """
        assert ref, 'must provide ref'
        # bibleref object (RangeVerseref or Verseref)
        self.ref = bibleref.makeBiblerefFromDTR(ref)
        self.bookname = unicode(self.ref.GetBookname())
        self.book = bible.BookForName(self.bookname)
        assert title, 'must provide title'
        self.title = unicode(title)
        # need a method to set next/previous
        # for tracking pericope sequence: only defined within a book
        # self.bookindex = None
        # self.next = None
        # self.previous = None

    # this encoding foo is probably the wrong approach
    def __repr__(self):
        return "{}('{}', '{}')".format(type(self).__name__, self.ref.ldlsref().encode('utf-8'),
                                   self.title.encode('utf-8'))

    def __unicode__(self):
        return u"%s('%s', '%s')" % (type(self).__name__, self.ref.ldlsref(),
                                   self.title)

    @property
    def start(self): return self.ref.start
        
    @property
    def end(self): return self.ref.end

    def set_sequence(self):
        pass
        
    def to_dict(self):
        """Return a dict of values to convert a Pericope to a Treemap.Mappable.
        """
        return {'id': unicode(self.ref.id),
                'label': unicode(self.ref.ldlsref()),
                'size': len(self.ref),
                'bookindex': self.bookindex,
                'bookname': self.bookname,
                'title': self.title,
                'previous': unicode(self.previous.ref.id) if self.previous else None,
                'next': unicode(self.next.ref.id) if self.next else None,
                }
# removed code from libronix.data related to treemaps


class PericopeSet(dict):
    """Models a complete set of pericopes. 
    """
    # YMMV
    userhomedir = Path(os.path.expanduser('~'))
    pdir =  userhomedir / 'git/ci/ShipPericopes/legacy/'

    def __init__(self, pericopeclass=Pericope):
        """Supply a subclass of Pericope for PERICOPECLASS if you want different
        treemap behavior.
        """
        dict.__init__(self)
        self.pericopeclass = pericopeclass
        # VerseRef -> Pericope
        # ToDo: use an OrderedDict and toss all this next/previous stuff, add an index within book
        
        self._pericopes = {}
        # first pericope of them all
        self.start = None
        # book -> first pericope, for all books
        self.book_starts = {}

    # ToDo: this is really slow with the API hits. Maybe go back to bibleref? 
    
    # the version that justs hashes every verse index to a pericope
    # that contains it
    def read(self, pdir=None, file='PericopesForSearch.xml'):
        if pdir:
            self.pdir = pdir
        self.path = os.path.join(self.pdir, file)
        pstr = etree.parse(open(self.path))
        lastp = None
        lastbook = None
        # assumption is that we're reading them in canonical order
        for el in pstr.xpath('/pericopes/*'):
            newp = self.pericopeclass(ref=el.xpath('string(@ref)'),
                            title=el.xpath('string(title)'))
            newbook = newp.bookname
            # this assumes the pericopes are read in order
            if not self.start:
                self.start = newp
            if newbook != lastbook:
                self.book_starts[newbook] = newp
                bookindex = 0
                lastbook = newbook
            else:
                bookindex += 1
            newp.bookindex = bookindex
            self[newp.ref] = newp
            start = newp.start
            end = newp.end
            # for vr in newp.ref.EnumerateVerses():
            #     self._pericopes[vr] = newp
            # cache results for development: API is slow
            if newp.ref not in _REFERENCE_CACHE:
                _REFERENCE_CACHE[newp.ref] = list(ru.enumerate_verses(newp.ref))
            for vr in _REFERENCE_CACHE[newp.ref]:
                self._pericopes[vr] = newp
            # add sequence information
            if lastp:
                newp.previous = lastp
                lastp.next = newp
            lastp = newp

    def find(self, bref):
        """Return the list of pericopes that span BREF, a VerseRef or
        RangeVerseref. Raise an IndexError if none can be matched.
        """
        assert isinstance(bref, bibleref.RangeVerseref) or isinstance(bref, bibleref.Verseref), \
          'Not a (Range)Verseref object: %s' % bref
        if isinstance(bref, bibleref.RangeVerseref):
            start = bref.start
            end = bref.end
        elif isinstance(bref, bibleref.Verseref):
            start = bref
            end = bref
        else:
            raise TypeError('Not a (Range)Verseref object: %s' % bref)
        try:
            startp = self._pericopes[start]
            endp = self._pericopes[end]
            pericopes = [startp]
            # since we've included all pericopes and they're
            # sequenced, move forward from the start until you hit the
            # end, then you've got them all
            try:
                while startp.ref < endp.ref:
                    startp = startp.next
                    pericopes.append(startp)
                return pericopes
            except:
                raise ValueError('Failed collecting pericopes for %s' % bref)
        except:
            raise KeyError('No pericopes matching %s and %s' % (start, end))

    def write_as_json(self, outstr):
        """Write pericope data as JSON to outstr. """
        start = self.start
        pdicts = []
        while start.next:
            pdicts.append(start.to_dict())
            start = start.next
        json.dump(pdicts, outstr, indent=2, sort_keys=True)




