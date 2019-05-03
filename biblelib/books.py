"""Library for working with Bible book information

>>> from biblelib import books
>>> books.Book('Mk')
<BibleBook: 62 (Mark)>
# simple checking of book index
>>> books.Book(91)
AssertionError: Invalid book index {}: must be in range 1 <= arg <= 87

>>> mark = books.Book('Mk')
# chapters and their final verses
>>> mark.finalverses
{1: 45, 2: 28, 3: 35, 4: 41, 5: 43, 6: 56, 7: 37, 8: 38, 9: 50, 10: 52, 11: 33, 12: 44, 13: 37, 14: 72, 15: 47, 16: 20}

## vindex

The vindex of a verse is its position in the sequence of all the verses
in a book, disregarding chapter boundaries. Example: the first chapter
of Mark has 45 verses. So the vindex of Mark 1:1 = 1, and for Mark 2:2
the vindex is 47 (45 + 2).

Consequently:
- vindex is only defined within the range of an individual book.
- vindex is not defined for whole-chapter references (like bible.62.2)
and chapter ranges (like bible.62.2-62.3)
- vindex does not handle other Bible data types than 'bible.'

# zero-based sequence index
>>> mark.get_vindex(4, 8)
115
# converted back
>>> mark.get_vindex_chapter_verse(115)
(4, 8)
>>> mark.get_vindex_dtr(115)
'bible.62.4.8'

TODO:
- rewrite BibleBook using dataclasses?

'"""

from collections import defaultdict


# maps abbreviations to BibleBook instances
_booknames = dict()


def Book(arg):
    """Return the Bible book matching arg

    With integer in range 1-87, return the book with that numeric index,
    otherwise an error.

    With name matching a standard abbreviation, return the book with
    that abbreviation, otherwise an error.
    """
    if isinstance(arg, int):
        assert arg >= 1 and arg <= 87, \
          f"Invalid book index: {arg} must be in range 1 <= arg <= 87"
        return _books[arg]
    elif isinstance(arg, str):
        assert arg in _booknames, f"Invalid book name: {arg}"
        return _booknames.get(arg)
    else:
        raise ValueError('Invalid arg type, must be int or str: {}'.format(arg))


class BibleBook(object):
    """Information about a book of the Bible."""
    # list of possible name types for validation
    nametypes = ['fullname', 'shortname', 'ldlsrefname', 'etdname']
    # the fuller set: i'm supporting only a subset for now
    # canon_traditions = ['Catholic', 'Ethiopian', 'Jewish', 'Orthodox', 'Protestant',
    #                     'Samaritan', 'Syriac']
    canon_traditions = ['Catholic', 'Jewish', 'Protestant']
    
    def __init__(self, index, fullname, shortname, ldlsref, etdname, alternates,
                 finalverses):
        self.index = index              # integer index for sorting
        self.fullname = fullname        # a full name ('1 Kings')
        self.shortname = shortname      # a brief name ('1Kgs')
        self.ldlsrefname = ldlsref      # name abbreviation used in ref attribute of <data> elements ('1 Ki')
        self.etdname = etdname          # name abbreviation used in Text Development  ('1Ki')
        # deprecated, but retained for backward compatibility
        self.ldlsref = ldlsref          
        self.alternates = alternates
        self.finalverses = finalverses  # chapter index -> final verse index
        self.n_chapters = len(self.finalverses)
        #self.group = None
        # running total of verses per chapter
        self.vindexdict = defaultdict(int)
        vsum = 0
        self.vindexdict[0] = 0
        for chapter, verse in self.finalverses.items():
            vsum += verse
            self.vindexdict[chapter] = vsum
        # the total number of verses for vindex checking
        self.n_verses = vsum
        self.canons = self.assign_canons()
        

    def __cmp__(self, other):
        return cmp(self.index, other.index)

    def __str__(self):
        return self.shortname

    def __repr__(self):
        return "<BibleBook: {} ({})>".format(self.index, self.shortname)

    def get_names(self):
        """Return a set of book names. """
        return set([self.fullname, self.shortname, self.ldlsrefname, self.etdname])
        
    def get_chapters(self):
        """Return a list of chapter indices, in order"""
        return sorted(self.finalverses.keys())
        
    def has_chapter(self, chapter):
        """Does SELF have a chapter matching CHAPTER?"""
        if isinstance(chapter, str):
            chapter = int(chapter)
        return chapter in self.finalverses

    def has_chapterandverse(self, chapter, verse):
        """Does SELF have a chapter and verse?

        Assumes verses from 1 to final verse.
        """
        if isinstance(chapter, str):
            chapter = int(chapter)
        if isinstance(verse, str):
            verse = int(verse)
        return (self.has_chapter(chapter) and
                verse <= self.get_finalverse(chapter))

    def get_bookname(self, nametype='shortname'):
        """Return the nametype name for this book. """
        assert nametype in self.nametypes, \
               "Nametype '%s' should be an element of %s" % (nametype, bible.nametypes)
        return getattr(self, nametype)

    def get_finalverse(self, chapter):
        """Return the index of the final verse for SELF and CHAPTER
        (also an integer index). WARNING: this depends on a global
        table of verses per chapter, but that's actually
        resource-specific: so this is only approximate."""
        return self.finalverses[chapter]
    
    def get_finalchapter(self):
        """Return the index of the final chapter."""
        return max(self.finalverses.keys())

    def get_vindex(self, chapter, verse):
        """Return the zero-based vindex for chapter and verse."""
        chapter = int(chapter)
        verse = int(verse)
        vindex = (self.vindexdict.get(chapter-1) + verse) - 1
        assert vindex < self.n_verses, \
          'Verse {} exceeds the index for chapter {}'.format(chapter, verse)
        return vindex

    def get_vindex_chapter_verse(self, vindex):
        """Return the Bible data type string for vindex."""
        pairs = [(c, v)for c,v in self.vindexdict.items()
                 if v < vindex]
        if pairs:
            c, v = max(pairs, key=lambda p: p[1])
            return (c + 1, vindex - v + 1)
        else:
            return (1, vindex + 1)

    def get_vindex_dtr(self, vindex):
        """Return the Bible data type string for vindex."""
        return "bible.{}.{}.{}".format(self.index, *self.get_vindex_chapter_verse(vindex))

    def assign_canons(self):
        """Return a set of canon names.

        See self.canon_traditions for the whole set.

        Traditions are only included for a book if it is 'fully' in the
        canon. Only BibleBooks are covered (so this won't tell you
        what's weird about the Ethiopian canon tradition).

        Logic taken from https://ref.ly/logos4/MediaTool?MediaItemId=247127
        """
        canons = set()
        # just the most dominant traditions for now
        if self.index <=39: canons.update(self.canon_traditions)
        if (40 <= self.index <= 60): canons.update(['Catholic'])
        if (61 <= self.index <= 87): canons.update(['Catholic', 'Protestant'])
        return canons

    def in_canon(self, tradition='Protestant'):
        assert tradition in self.canon_traditions, \
          "Tradition '{}' must be one of {}".format(tradition, self.canon_traditions)
        return tradition in self.canons


_books = [
    None,                               # so we can index from 1
    BibleBook(1, 'Genesis', 'Gen', 'Ge', 'Ge',
              ['Gen', 'Ge', 'Gn'],
              {1:31,2:25,3:24,4:26,5:32,6:22,7:24,8:22,9:29,10:32,11:32,12:20,13:18,14:24,15:21,16:16,17:27,18:33,19:38,20:18,21:34,22:24,23:20,24:67,25:34,26:35,27:46,28:22,29:35,30:43,31:55,32:32,33:20,34:31,35:29,36:43,37:36,38:30,39:23,40:23,41:57,42:38,43:34,44:34,45:28,46:34,47:31,48:22,49:33,50:26}),
    BibleBook(2, 'Exodus', 'Exod', 'Ex', 'Ex',
              ['Exo', 'Ex', 'Exod'],
               # bfc, danclv, other versions have 7:26
               # einheit has 21:37
              {1:22,2:25,3:22,4:31,5:23,6:30,7:26,8:32,9:35,10:29,11:10,12:51,13:22,14:31,15:27,16:36,17:16,18:27,19:25,20:26,21:37,22:31,23:33,24:18,25:40,26:37,27:21,28:43,29:46,30:38,31:18,32:35,33:23,34:35,35:35,36:38,37:29,38:31,39:43,40:38}),
    BibleBook(3, 'Leviticus', 'Lev', 'Le', 'Le',
              ['Lev', 'Le', 'Lv'],
              {1:17,2:16,3:17,4:35,5:19,6:30,7:38,8:36,9:24,10:20,11:47,12:8,13:59,14:57,15:33,16:34,17:16,18:30,19:37,20:27,21:24,22:33,23:44,24:23,25:55,26:46,27:34}),
    BibleBook(4, 'Numbers', 'Num', 'Nu', 'Nu',
              ['Num', 'Nu', 'Nm', 'Nb'],
              {1:54,2:34,3:51,4:49,5:31,6:27,7:89,8:26,9:23,10:36,11:35,12:16,13:33,14:45,15:41,16:50,17:13,18:32,19:22,20:29,21:35,22:41,23:30,24:25,25:19,26:65,27:23,28:31,29:40,30:16,31:54,32:42,33:56,34:29,35:34,36:13}),
    BibleBook(5, 'Deuteronomy', 'Deut', 'Dt', 'De',
              ['Deut', 'Dt', 'De'],
               # nbv has 5:44, seems too far out-of-scope
              {1:46,2:37,3:29,4:49,5:33,6:25,7:26,8:20,9:29,10:22,11:32,12:32,13:18,14:29,15:23,16:22,17:20,18:22,19:21,20:20,21:23,22:30,23:25,24:22,25:19,26:19,27:26,28:68,29:29,30:20,31:30,32:52,33:29,34:12}),
    BibleBook(6, 'Joshua', 'Josh', 'Jos', 'Jos',
              ['Josh', 'Jos', 'Jsh'],
              {1:18,2:24,3:17,4:24,5:15,6:27,7:26,8:35,9:27,10:43,11:23,12:24,13:33,14:15,15:63,16:10,17:18,18:28,19:51,20:9,21:45,22:34,23:16,24:33}),
    BibleBook(7, 'Judges', 'Judg', 'Jdg', 'Jdg',
              ['Judg', 'Jdg', 'Jg', 'Jdgs'],
              {1:36,2:23,3:31,4:24,5:31,6:40,7:25,8:35,9:57,10:18,11:40,12:15,13:25,14:20,15:20,16:31,17:13,18:31,19:30,20:48,21:25}),
    BibleBook(8, 'Ruth', 'Ruth', 'Ru', 'Ru',
              ['Rth', 'Ru'],
              {1:22,2:23,3:18,4:22}),
    # doesn't handle "1 Sam": should it?
    BibleBook(9, '1 Samuel', '1Sam', '1 Sa', '1Sa',
              ['1 Sam', '1 Sa', '1Samuel', '1S', 'I Sa', '1 Sm', '1Sa', 'I Sam', '1Sam', 'I Samuel', '1st Samuel', 'First Samuel'],
              {1:28,2:36,3:21,4:22,5:12,6:21,7:17,8:22,9:27,10:27,11:15,12:25,13:23,14:52,15:35,16:23,17:58,18:30,19:24,20:42,21:15,22:23,23:29,24:22,25:44,26:25,27:12,28:25,29:11,30:31,31:13}),
    BibleBook(10, '2 Samuel', '2Sam', '2 Sa', '2Sa',
              ['2 Sam', '2 Sa', '2S', 'II Sa', '2 Sm', '2Sa', 'II Sam', '2Sam', 'II Samuel', '2Samuel', '2nd Samuel', 'Second Samuel'],
              {1:27,2:32,3:39,4:12,5:25,6:23,7:29,8:18,9:13,10:19,11:27,12:31,13:39,14:33,15:37,16:23,17:29,18:33,19:43,20:26,21:22,22:51,23:39,24:25}),
    BibleBook(11, '1 Kings', '1Kgs', '1 Ki', '1Ki',
              ['1 Kgs', '1 Ki', '1K', 'I Kgs', '1Kgs', 'I Ki', '1Ki', 'I Kings', '1Kings', '1st Kgs', '1st Kings', 'First Kings', 'First Kgs', '1Kin'],
              {1:53,2:46,3:28,4:34,5:18,6:38,7:51,8:66,9:28,10:29,11:43,12:33,13:34,14:31,15:34,16:34,17:24,18:46,19:21,20:43,21:29,22:53}),
    BibleBook(12, '2 Kings', '2Kgs', '2 Ki', '2Ki',
              ['2 Kgs', '2 Ki', '2K', 'II Kgs', '2Kgs', 'II Ki', '2Ki', 'II Kings', '2Kings', '2nd Kgs', '2nd Kings', 'Second Kings', 'Second Kgs', '2Kin'],
              {1:18,2:25,3:27,4:44,5:27,6:33,7:20,8:29,9:37,10:36,11:21,12:21,13:25,14:29,15:38,16:20,17:41,18:37,19:37,20:21,21:26,22:20,23:37,24:20,25:30}),
    BibleBook(13, '1 Chronicles', '1Chr', '1 Ch', '1Ch',
              ['1 Chron', '1 Ch', 'I Ch', '1Ch', '1 Chr', 'I Chr', '1Chr', 'I Chron', '1Chron', 'I Chronicles', '1Chronicles', '1st Chronicles', 'First Chronicles'],
              {1:54,2:55,3:24,4:43,5:26,6:81,7:40,8:40,9:44,10:14,11:47,12:40,13:14,14:17,15:29,16:43,17:27,18:17,19:19,20:8,21:30,22:19,23:32,24:31,25:31,26:32,27:34,28:21,29:30}),
    BibleBook(14, '2 Chronicles', '2Chr', '2 Ch', '2Ch',
              ['2 Chron', '2 Ch', 'II Ch', '2Ch', '2 Chr', 'II Chr', '2Chr', 'II Chron', '2Chron', 'II Chronicles', '2Chronicles', '2nd Chronicles', 'Second Chronicles'],
              {1:17,2:18,3:17,4:22,5:14,6:42,7:22,8:18,9:31,10:19,11:23,12:16,13:22,14:15,15:19,16:14,17:19,18:34,19:11,20:37,21:20,22:12,23:21,24:27,25:28,26:23,27:9,28:27,29:36,30:27,31:21,32:33,33:25,34:33,35:27,36:23}),
    BibleBook(15, 'Ezra', 'Ezra', 'Ezr', 'Ezr',
              ['Ezra', 'Ezr'],
              {1:11,2:70,3:13,4:24,5:17,6:22,7:28,8:36,9:15,10:44}),
    BibleBook(16, 'Nehemiah', 'Neh', 'Ne', 'Ne',
              ['Neh', 'Ne'],
              {1:11,2:20,3:32,4:23,5:19,6:19,7:73,8:18,9:38,10:39,11:36,12:47,13:31}),
    BibleBook(17, 'Esther', 'Esth', 'Es', 'Es',
              ['Esth', 'Es', 'Est'],
              {1:22,2:23,3:15,4:17,5:14,6:14,7:10,8:17,9:32,10:3}),
    BibleBook(18, 'Job', 'Job', 'Job', 'Job',
              ['Job', 'Job', 'Jb'],
              {1:22,2:13,3:26,4:21,5:27,6:30,7:21,8:22,9:35,10:22,11:20,12:25,13:28,14:22,15:35,16:22,17:16,18:21,19:29,20:29,21:34,22:30,23:17,24:25,25:6,26:14,27:23,28:28,29:25,30:31,31:40,32:22,33:33,34:37,35:16,36:33,37:24,38:41,39:30,40:24,41:34,42:17}),
    # 2nd element was 'Ps', now 'Psalm' to have it both ways
    BibleBook(19, 'Psalms', 'Psalm', 'Ps', 'Ps',
              ['Pslm', 'Ps', 'Psalms', 'Psa', 'Psm', 'Pss'],
              {1:6,2:12,3:8,4:8,5:12,6:10,7:17,8:9,9:20,10:18,11:7,12:8,13:6,14:7,15:5,16:11,17:15,18:50,19:14,20:9,21:13,22:31,23:6,24:10,25:22,26:12,27:14,28:9,29:11,30:12,31:24,32:11,33:22,34:22,35:28,36:12,37:40,38:22,39:13,40:17,41:13,42:11,43:5,44:26,45:17,46:11,47:9,48:14,49:20,50:23,51:19,52:9,53:6,54:7,55:23,56:13,57:11,58:11,59:17,60:12,61:8,62:12,63:11,64:10,65:13,66:20,67:7,68:35,69:36,70:5,71:24,72:20,73:28,74:23,75:10,76:12,77:20,78:72,79:13,80:19,81:16,82:8,83:18,84:12,85:13,86:17,87:7,88:18,89:52,90:17,91:16,92:15,93:5,94:23,95:11,96:13,97:12,98:9,99:9,100:5,101:8,102:28,103:22,104:35,105:45,106:48,107:43,108:13,109:31,110:7,111:10,112:10,113:9,114:8,115:18,116:19,117:2,118:29,119:176,120:7,121:8,122:9,123:4,124:8,125:5,126:6,127:5,128:6,129:8,130:8,131:3,132:18,133:3,134:3,135:21,136:26,137:9,138:8,139:24,140:13,141:10,142:7,143:12,144:15,145:21,146:10,147:20,148:14,149:9,150:6}),
    BibleBook(20, 'Proverbs', 'Prov', 'Pr', 'Pr',
              ['Prov', 'Pr', 'Prv'],
              {1:33,2:22,3:35,4:27,5:23,6:35,7:27,8:36,9:18,10:32,11:31,12:28,13:25,14:35,15:33,16:33,17:28,18:24,19:29,20:30,21:31,22:29,23:35,24:34,25:28,26:28,27:27,28:28,29:27,30:33,31:31}),
    BibleBook(21, 'Ecclesiastes', 'Eccl', 'Ec', 'Ec',
              ['Eccles', 'Ec', 'Qoh', 'Qoheleth'],
              {1:18,2:26,3:22,4:17,5:20,6:12,7:29,8:17,9:18,10:20,11:10,12:14}),
    BibleBook(22, 'Song of Solomon', 'Song', 'So', 'So',
              ['So', 'Canticle of Canticles', 'Canticles', 'Song of Songs', 'SOS', 'Sng'],
              {1:17,2:17,3:11,4:16,5:16,6:13,7:13,8:14}),
    BibleBook(23, 'Isaiah', 'Isa', 'Is', 'Is',
              ['Isa', 'Is'],
              {1:31,2:22,3:26,4:6,5:30,6:13,7:25,8:23,9:21,10:34,11:16,12:6,13:22,14:32,15:9,16:14,17:14,18:7,19:25,20:6,21:17,22:25,23:18,24:23,25:12,26:21,27:13,28:29,29:24,30:33,31:9,32:20,33:24,34:17,35:10,36:22,37:38,38:22,39:8,40:31,41:29,42:25,43:28,44:28,45:25,46:13,47:15,48:22,49:26,50:11,51:23,52:15,53:12,54:17,55:13,56:12,57:21,58:14,59:21,60:22,61:11,62:12,63:19,64:12,65:25,66:24}),
    BibleBook(24, 'Jeremiah', 'Jer', 'Je', 'Je',
              ['Jer', 'Je', 'Jr'],
              {1:19,2:37,3:25,4:31,5:31,6:30,7:34,8:22,9:26,10:25,11:23,12:17,13:27,14:22,15:21,16:21,17:27,18:23,19:15,20:18,21:14,22:30,23:40,24:10,25:38,26:24,27:22,28:17,29:32,30:24,31:40,32:44,33:26,34:22,35:19,36:32,37:21,38:28,39:18,40:16,41:18,42:22,43:13,44:30,45:5,46:28,47:7,48:47,49:39,50:46,51:64,52:34}),
    BibleBook(25, 'Lamentations', 'Lam', 'La', 'La',
              ['Lam', 'La'],
              {1:22,2:22,3:66,4:22,5:22}),
    BibleBook(26, 'Ezekiel', 'Ezek', 'Eze', 'Eze',
              ['Ezek', 'Eze', 'Ezk'],
              {1:28,2:10,3:27,4:17,5:17,6:14,7:27,8:18,9:11,10:22,11:25,12:28,13:23,14:23,15:8,16:63,17:24,18:32,19:14,20:49,21:32,22:31,23:49,24:27,25:17,26:21,27:36,28:26,29:21,30:26,31:18,32:32,33:33,34:31,35:15,36:38,37:28,38:23,39:29,40:49,41:26,42:20,43:27,44:31,45:25,46:24,47:23,48:35}),
    BibleBook(27, 'Daniel', 'Dan', 'Da', 'Da',
              ['Dan', 'Da', 'Dn'],
              {1:21,2:49,3:30,4:37,5:31,6:28,7:28,8:27,9:27,10:21,11:45,12:13}),
    BibleBook(28, 'Hosea', 'Hos', 'Ho', 'Ho',
              ['Hos', 'Ho'],
              {1:11,2:23,3:5,4:19,5:15,6:11,7:16,8:14,9:17,10:15,11:12,12:14,13:16,14:9}),
    BibleBook(29, 'Joel', 'Joel', 'Joe', 'Joe',
              ['Joel', 'Joe', 'Jl'],
              {1:20,2:32,3:21}),
    BibleBook(30, 'Amos', 'Amos', 'Am', 'Am',
              ['Amos', 'Am'],
              {1:15,2:16,3:15,4:13,5:27,6:14,7:17,8:14,9:15}),
    BibleBook(31, 'Obadiah', 'Obad', 'Obad', 'Ob',
              ['Obad', 'Ob'],
              {1:21}),
    BibleBook(32, 'Jonah', 'Jonah', 'Jon', 'Jon',
              ['Jnh', 'Jon'],
              {1:17,2:10,3:10,4:11}),
    BibleBook(33, 'Micah', 'Mic', 'Mic', 'Mic',
              ['Micah', 'Mic'],
              {1:16,2:13,3:12,4:14,5:15,6:16,7:20}),
    BibleBook(34, 'Nahum', 'Nah', 'Na', 'Na',
              ['Nah', 'Na'],
              {1:15,2:13,3:19}),
    BibleBook(35, 'Habakkuk', 'Hab', 'Hab', 'Hab',
              ['Hab', 'Hab'],
              {1:17,2:20,3:19}),
    BibleBook(36, 'Zephaniah', 'Zeph', 'Zep', 'Zep',
              ['Zeph', 'Zep', 'Zp'],
              {1:18,2:15,3:20}),
    BibleBook(37, 'Haggai', 'Hag', 'Hag', 'Hag',
              ['Haggai', 'Hag', 'Hg'],
              {1:15,2:23}),
    BibleBook(38, 'Zechariah', 'Zech', 'Zec', 'Zec',
              ['Zech', 'Zec', 'Zc'],
              {1:21,2:13,3:10,4:14,5:11,6:15,7:14,8:23,9:17,10:12,11:17,12:14,13:9,14:21}),
    BibleBook(39, 'Malachi', 'Mal', 'Mal', 'Mal',
              ['Mal', 'Mal', 'Ml'],
              {1:14,2:17,3:18,4:6}),
    BibleBook(40, 'Tobit', 'Tob', 'Tob', 'Tob',
              ['Tobit', 'Tob', 'Tb'],
              {1:22,2:14,3:16,4:21,5:22,6:18,7:16,8:21,9:6,10:13,11:18,12:22,13:17,14:15}),
    BibleBook(41, 'Judith', 'Jdt', 'Jdt', 'Jdt',
              ['Jdth', 'Jdt', 'Jth'],
              {1:16,2:28,3:10,4:15,5:24,6:21,7:32,8:36,9:14,10:23,11:23,12:20,13:20,14:19,15:14,16:20}),
    BibleBook(42, 'Additions to Esther', 'AddEsth', 'Add Es', 'Add Es',
              ['AddEsth', 'Add Esth', 'Add Est', 'Add Es', 'Rest of Esther', 'The Rest of Esther', 'AEs', 'AddEsth'],
              {1:22,2:23,3:15,4:17,5:14,6:14,7:10,8:17,9:32,10:13,11:12,12:6,13:18,14:19,15:16,16:24}),
    BibleBook(43, 'Wisdom of Solomon', 'Wis', 'Wis', 'Wis',
              ['Wisd of Sol', 'Wis', 'Ws', 'Wisdom'],
              {1:16,2:24,3:19,4:20,5:23,6:25,7:30,8:21,9:18,10:21,11:26,12:27,13:19,14:31,15:19,16:29,17:21,18:25,19:22}),
    BibleBook(44, 'Sirach', 'Sir', 'Sir', 'Sir',
              ['Sirach', 'Sir', 'Ecclesiasticus', 'Ecclus'],
              {1:30,2:17,3:31,4:31,5:15,6:37,7:36,8:19,9:18,10:31,11:34,12:18,13:26,14:27,15:20,16:30,17:32,18:33,19:30,20:31,21:28,22:27,23:27,24:34,25:26,26:29,27:30,28:26,29:28,30:25,31:31,32:24,33:33,34:31,35:26,36:31,37:31,38:34,39:35,40:30,41:22,42:25,43:33,44:23,45:26,46:20,47:25,48:25,49:16,50:29,51:30}),
    BibleBook(45, 'Baruch', 'Bar', 'Bar', 'Bar',
              ['Baruch', 'Bar'],
              {1:22,2:35,3:37,4:37,5:9,6:73}),
    # this used to have EpJer as the lsldref, but the parser won't take it
    BibleBook(46, 'Letter of Jeremiah', 'EpJer', 'LJe', 'Lje',
              ['EpJer', 'Let Jer', 'LJe', 'Ltr Jer'],
              {6:73}),
    BibleBook(47, 'Song of Three Youths', 'SgThree', 'Song Thr', 'Pr Az',
              ['Three Youths', 'SgThree', 'Song of Three', 'Song Thr', 'The Song of Three Youths', 'Pr Az', 'Prayer of Azariah', 'Azariah', 'The Song of the Three Holy Children', 'The Song of Three Jews', 'Song of the Three Holy Children', 'Song of Thr', 'Song of Three Children', 'Song of Three Jews'],
              {1:68}),
    BibleBook(48, 'Susanna', 'Sus', 'Sus', 'Sus',
              ['Susanna', 'Sus'],
              {1:63}),
    BibleBook(49, 'Bel and the Dragon', 'Bel', 'Bel', 'Bel',
              ['Bel'],
              {1:42}),
    BibleBook(50, '1 Maccabees', '1Macc', '1 Mac', '1Ma',
              ['1 Macc', '1 Mac', '1M', 'I Ma', '1Ma', 'I Mac', '1Mac', 'I Macc', '1Macc', 'I Maccabees', '1Maccabees', '1st Maccabees', 'First Maccabees'],
              {1:64,2:70,3:60,4:61,5:68,6:63,7:50,8:32,9:73,10:89,11:74,12:53,13:53,14:49,15:41,16:24}),
    BibleBook(51, '2 Maccabees', '2Macc', '2 Mac', '2Ma',
              ['2 Macc', '2 Mac', '2M', 'II Ma', '2Ma', 'II Mac', '2Mac', 'II Macc', '2Macc', 'II Maccabees', '2Maccabees', '2nd Maccabees', 'Second Maccabees'],
              {1:36,2:32,3:40,4:50,5:27,6:31,7:42,8:36,9:28,10:38,11:38,12:45,13:26,14:46,15:39}),
    BibleBook(52, '1 Esdras', '1Esd', '1 Esd', '1Es',
              ['1 Esdr', '1 Esd', 'I Es', '1Es', 'I Esd', '1Esd', 'I Esdr', '1Esdr', 'I Esdras', '1Esdras', '1st Esdras', 'First Esdras'],
              {1:58,2:30,3:24,4:63,5:73,6:34,7:15,8:96,9:55}),
    BibleBook(53, 'Prayer of Manasseh', 'PrMan', 'PrMan', 'Pr Man',
              ['Pr of Man', 'Pr Man', 'PMa', 'Prayer of Manasses'],
              {1:15}),
    BibleBook(54, 'Additional Psalm', 'AddPs', 'AddPs', 'Add Ps',
              ['Add Psalm', 'Add Ps'],
              {1:7}),
    BibleBook(55, '3 Maccabees', '3Macc', '3 Mac', '3Ma',
              ['3 Macc', '3 Mac', 'III Ma', '3Ma', 'III Mac', '3Mac', 'III Macc', '3Macc', 'III Maccabees', '3rd Maccabees', 'Third Maccabees'],
              {1:29,2:33,3:30,4:21,5:51,6:41,7:23}),
    BibleBook(56, '2 Esdras', '2Esd', '2 Esd', '2Es',
              ['2 Esdr', '2 Esd', 'II Es', '2Es', 'II Esd', '2Esd', 'II Esdr', '2Esdr', 'II Esdras', '2Esdras', '2nd Esdras', 'Second Esdras'],
              {1:40,2:48,3:36,4:52,5:56,6:59,7:140,8:63,9:47,10:59,11:46,12:51,13:58,14:48,15:63,16:78}),
    BibleBook(57, '4 Maccabees', '4Macc', '4 Mac', '4Ma',
              ['4 Macc', '4 Mac', 'IV Ma', '4Ma', 'IV Mac', '4Mac', 'IV Macc', '4Macc', 'IV Maccabees', 'IIII Maccabees', '4Maccabees', '4th Maccabees', 'Fourth Maccabees'],
              {1:35,2:24,3:21,4:26,5:38,6:35,7:23,8:29,9:31,10:21,11:27,12:19,13:27,14:20,15:32,16:25,17:24,18:24}),
    # don't know the etdnames for 58-60, assuming the same as ldlfrefname
    BibleBook(58, 'Ode', 'Ode', 'Ode', 'Ode',
              ['Ode', 'Ode'],
              # not sure this information is reliable
              {1:5,3:11,4:15,5:15,6:18,7:26,8:22,9:12,10:6,11:24,12:13,13:4,14:10,15:10,16:20,17:17,18:16,19:11,20:10,21:9,22:12,23:22,24:14,25:12,26:13,27:3,28:20,29:11,30:7,31:13,32:3,33:13,34:6,35:7,36:8,37:4,38:22,39:13,40:6,41:16,42:20}),
    BibleBook(59, 'Psalms of Solomon', 'PsSol', 'PsSol', 'PsSol',
              ['Ps Solomon', 'Ps Sol', 'Psalms Solomon', 'PsSol'],
              {1:8,2:37,3:12,4:25,5:19,6:6,7:10,8:34,9:11,10:8,11:9,12:6,13:12,14:10,15:13,16:15,17:46,18:12}),
    BibleBook(60, 'Epistle to the Laodiceans', 'EpLaod', 'EpLaod', 'EpLaod',
              ['Laodiceans', 'Laod', 'Ep Laod', 'Epist Laodiceans', 'Epistle Laodiceans', 'Epistle to Laodiceans'],
              {1:19}),
    BibleBook(61, 'Matthew', 'Matt', 'Mt', 'Mt',
              ['Matt', 'Mt'],
              {1:25,2:23,3:17,4:25,5:48,6:34,7:29,8:34,9:38,10:42,11:30,12:50,13:58,14:36,15:39,16:28,17:27,18:35,19:30,20:34,21:46,22:46,23:39,24:51,25:46,26:75,27:66,28:20}),
    BibleBook(62, 'Mark', 'Mark', 'Mk', 'Mk',
              ['Mrk', 'Mk', 'Mr'],
              {1:45,2:28,3:35,4:41,5:43,6:56,7:37,8:38,9:50,10:52,11:33,12:44,13:37,14:72,15:47,16:20}),
    BibleBook(63, 'Luke', 'Luke', 'Lk', 'Lu',
              ['Luk', 'Lk'],
              {1:80,2:52,3:38,4:44,5:39,6:49,7:50,8:56,9:62,10:42,11:54,12:59,13:35,14:35,15:32,16:31,17:37,18:43,19:48,20:47,21:38,22:71,23:56,24:53}),
    BibleBook(64, 'John', 'John', 'Jn', 'Jn',
              ['John', 'Jn', 'Jhn'],
              {1:51,2:25,3:36,4:54,5:47,6:71,7:53,8:59,9:41,10:42,11:57,12:50,13:38,14:31,15:27,16:33,17:26,18:40,19:42,20:31,21:25}),
    BibleBook(65, 'Acts', 'Acts', 'Ac', 'Ac',
              ['Acts', 'Ac'],
              {1:26,2:47,3:26,4:37,5:42,6:15,7:60,8:40,9:43,10:48,11:30,12:25,13:52,14:28,15:41,16:40,17:34,18:28,19:41,20:38,21:40,22:30,23:35,24:27,25:27,26:32,27:44,28:31}),
    BibleBook(66, 'Romans', 'Rom', 'Ro', 'Ro',
              ['Rom', 'Ro', 'Rm'],
              {1:32,2:29,3:31,4:25,5:21,6:23,7:25,8:39,9:33,10:21,11:36,12:21,13:14,14:23,15:33,16:27}),
    BibleBook(67, '1 Corinthians', '1Cor', '1 Co', '1Co',
              ['1 Cor', '1 Co', 'I Co', '1Co', 'I Cor', '1Cor', 'I Corinthians', '1Corinthians', '1st Corinthians', 'First Corinthians', '1 Cor'],
              {1:31,2:16,3:23,4:21,5:13,6:20,7:40,8:13,9:27,10:33,11:34,12:31,13:13,14:40,15:58,16:24}),
    BibleBook(68, '2 Corinthians', '2Cor', '2 Co', '2Co',
              ['2 Cor', '2 Co', 'II Co', '2Co', 'II Cor', '2Cor', 'II Corinthians', '2Corinthians', '2nd Corinthians', 'Second Corinthians', '2 Cor'],
              {1:24,2:17,3:18,4:18,5:21,6:18,7:16,8:24,9:15,10:18,11:33,12:21,13:14}),
    BibleBook(69, 'Galatians', 'Gal', 'Ga', 'Ga',
              ['Gal', 'Ga'],
              {1:24,2:21,3:29,4:31,5:26,6:18}),
    BibleBook(70, 'Ephesians', 'Eph', 'Eph', 'Eph',
              ['Ephes', 'Eph'],
              {1:23,2:22,3:21,4:32,5:33,6:24}),
    BibleBook(71, 'Philippians', 'Phil', 'Php', 'Php',
              ['Phil', 'Php'],
              {1:30,2:30,3:21,4:23}),
    BibleBook(72, 'Colossians', 'Col', 'Col', 'Col',
              ['Col', 'Col'],
              {1:29,2:23,3:25,4:18}),
    BibleBook(73, '1 Thessalonians', '1Thess', '1 Th', '1Th',
              ['1 Thess', '1 Th', 'I Th', '1Th', 'I Thes', '1 Thes', '1Thes', 'I Thess', '1Thess', 'I Thessalonians', '1Thessalonians', '1st Thessalonians', 'First Thessalonians'],
              {1:10,2:20,3:13,4:18,5:28}),
    BibleBook(74, '2 Thessalonians', '2Thess', '2 Th', '2Th',
              ['2 Thess', '2 Th', 'II Th', '2Th', 'II Thes', '2 Thes', '2Thes', 'II Thess', '2Thess', 'II Thessalonians', '2Thessalonians', '2nd Thessalonians', 'Second Thessalonians'],
              {1:12,2:17,3:18}),
    BibleBook(75, '1 Timothy', '1Tim', '1 Ti', '1Ti',
              ['1 Ti', '1 Ti', 'I Ti', '1Ti', 'I Tim', '1Tim', 'I Timothy', '1Timothy', '1st Timothy', 'First Timothy', '1 Tim'],
              {1:20,2:15,3:16,4:16,5:25,6:21}),
    BibleBook(76, '2 Timothy', '2Tim', '2 Ti', '2Ti',
              ['2 Ti', '2 Ti', 'II Ti', '2Ti', 'II Tim', '2Tim', 'II Timothy', '2Timothy', '2nd Timothy', 'Second Timothy', '2 Tim'],
              {1:18,2:26,3:17,4:22}),
    BibleBook(77, 'Titus', 'Titus', 'Tt', 'Tt',
              ['Titus', 'Tit'],
              {1:16,2:15,3:15}),
    BibleBook(78, 'Philemon', 'Phlm', 'Phm', 'Phm',
              ['Philem', 'Phm'],
              {1:25}),
    BibleBook(79, 'Hebrews', 'Heb', 'Heb', 'Heb',
              ['Hebrews', 'Heb'],
              {1:14,2:18,3:19,4:16,5:14,6:20,7:28,8:13,9:28,10:39,11:40,12:29,13:25}),
    BibleBook(80, 'James', 'Jas', 'Jas', 'Jam',
              ['James', 'Jas', 'Jm'],
              {1:27,2:26,3:18,4:17,5:20}),
    BibleBook(81, '1 Peter', '1Pet', '1 Pe', '1Pe',
              ['1 Pet', '1 Pe', 'I Pe', '1Pe', 'I Pet', '1Pet', 'I Pt', '1 Pt', '1Pt', 'I Peter', '1Peter', '1st Peter', 'First Peter'],
              {1:25,2:25,3:22,4:19,5:14}),
    BibleBook(82, '2 Peter', '2Pet', '2 Pe', '2Pe',
              ['2 Pet', '2 Pe', 'II Pe', '2Pe', 'II Pet', '2Pet', 'II Pt', '2 Pt', '2Pt', 'II Peter', '2Peter', '2nd Peter', 'Second Peter'],
              {1:21,2:22,3:18}),
    BibleBook(83, '1 John', '1John', '1 Jn', '1Jn',
              ['1 John', '1 Jn', 'I Jn', '1Jn', 'I Jo', '1Jo', 'I Joh', '1Joh', 'I Jhn', '1 Jhn', '1Jhn', 'I John', '1John', '1st John', 'First John'],
              {1:10,2:29,3:24,4:21,5:21}),
    BibleBook(84, '2 John', '2John', '2 Jn', '2Jn',
              ['2 John', '2 Jn', 'II Jn', '2Jn', 'II Jo', '2Jo', 'II Joh', '2Joh', 'II Jhn', '2 Jhn', '2Jhn', 'II John', '2John', '2nd John', 'Second John'],
              {1:13}),
    BibleBook(85, '3 John', '3John', '3 Jn', '3Jn',
              ['3 John', '3 Jn', 'III Jn', '3Jn', 'III Jo', '3Jo', 'III Joh', '3Joh', 'III Jhn', '3 Jhn', '3Jhn', 'III John', '3John', '3rd John', 'Third John'],
              {1:15}),
    BibleBook(86, 'Jude', 'Jude', 'Jud', 'Jud',
              ['Jude', 'Jud'],
              {1:25}),
    BibleBook(87, 'Revelation', 'Rev', 'Re', 'Rev',
              ['Rev', 'Re', 'The Revelation'],
              {1:20,2:29,3:22,4:11,5:14,6:17,7:17,8:13,9:21,10:11,11:19,12:18,13:18,14:20,15:8,16:21,17:18,18:24,19:21,20:15,21:27,22:21}),
    ]

# register in _booknames
for book in _books[1:]:
    for abbrevattr in ['fullname', 'shortname', 'ldlsrefname', 'etdname']:
        #print("{}, {}".format(book, abbrevattr))
        abbrev = getattr(book, abbrevattr)
        if abbrev in _booknames:
            if _booknames[abbrev] != book:
                warn("Overwriting _booknames[{}] with {}".format(abbrev, book))
        else:
            _booknames[abbrev] = book
        # also any alternates, but don't overwrite: this gets 1 Sam
        for alt in getattr(book, 'alternates'):
            if alt not in _booknames:
                _booknames[alt] = book
                


def get_all_booknames():
    "For building regexp reference matchers"
    return {name for book in _books[1:] for name in book.get_names() | set(book.alternates)}

    
# random data: these single verses are gaps in the the ESV numbering
# due to text critical decisions, though present in the (N)KJV
_missingverses = [
    'Mt 12.47',
    'Mt 17.21',
    'Mt 18.11',
    'Mk 15.28',
    'Lu 17.36',
    'Lu 23.17',
    'Ac 8.37',
    'Ac 24.6b',
    'Ac 24.7',
    'Ac 24.8a',
    'Ac 28.29',
    ]

    
