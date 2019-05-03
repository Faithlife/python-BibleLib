"""Groups of Bible books

>>> from logos_pyutil.bible import groups
# retrieve a group by name
>>> groups.groupnames['Gospels']
<BookGroup: Gospels>
>>> groups.groupnames.keys()
['Pentateuch', 'OT History', 'Poetry', 'Major Prophets', 'Minor Prophets',
'Apocrypha', 'Gospels', 'NT History', 'Pauline Epistles', 'Pastoral Epistles',
 'Catholic Epistles', 'Apocalypse']

# get the BibleBook objects for a BookGroup
>>> groups.groupnames['Gospels'].get_books()
[<BibleBook: 61 (Matt)>, <BibleBook: 62 (Mark)>, <BibleBook: 63 (Luke)>,
<BibleBook: 64 (John)>]
# roll up counts of chapters and verses
>>> groups.groupnames['Gospels'].n_chapters
89
>>> groups.groupnames['Gospels'].n_verses
3779

# get a list of book + chapter
>>> groups.groupnames['Pastoral Epistles'].get_book_chapters()
['1 Ti 1', '1 Ti 2', '1 Ti 3', '1 Ti 4', '1 Ti 5', '1 Ti 6', '2 Ti 1', '2 Ti 2',
 '2 Ti 3', '2 Ti 4', 'Tit 1', 'Tit 2', 'Tit 3', 'Phm 1']

"""

from collections import OrderedDict

from .books import Book


# maps names to BookGroup instances
groupnames = OrderedDict()


class BookGroup(object):
    """Information about a group of Bible books."""
    # the fuller set: i'm supporting only a subset for now
    # canon_traditions = ['Catholic', 'Ethiopian', 'Jewish', 'Orthodox',
    #                     'Protestant', 'Samaritan', 'Syriac']
    canon_traditions = ['Catholic', 'Jewish', 'Protestant']
    
    def __init__(self, name, booknames=[], subgroups=[]):
        self.name = name
        self.books = [Book(bookname) for bookname in booknames]
        self.n_chapters = sum(book.n_chapters for book in self.books)
        self.n_verses = sum(book.n_verses for book in self.books)
        # TODO: maybe use parent groups instead?
        # assert isinstance(subgroups, list), 'Subgroups must be a list: {}'.format(subgroups)
        # self.subgroups = subgroups
        self.canons = self.assign_canons()

        # self.finalverses = finalverses  # chapter index -> final verse index
        # #self.group = None
        # # running total of verses per chapter
        # self.vindexdict = defaultdict(int)
        # vsum = 0
        # self.vindexdict[0] = 0
        # for chapter, verse in self.finalverses.items():
        #     vsum += verse
        #     self.vindexdict[chapter] = vsum
        # # the total number of verses for vindex checking
        # self.n_verses = vsum
        
    def __str__(self):
        return self.name

    def __repr__(self):
        return "<BookGroup: {}>".format(self.name)

    def __len__(self):
        return len(self.get_books())
    
    def get_books(self):
        """Return a list of included BibleBook objects, in order"""
        return self.books
        
    def get_book_chapters(self):
        """Return a list of included book + chapter, in order"""
        return ["{} {}".format(book.ldlsref, chapter)
                for book in self.get_books()
                for chapter in book.get_chapters()]
        
    def assign_canons(self):
        """A group is in a canon if all books in the group are in a canon. 
        """
        canons = set()
        for canon in self.canon_traditions:
            if all(book.in_canon(canon) for book in self.get_books()):
                canons.update([canon])
        return canons

    def in_canon(self, tradition='Protestant'):
        assert tradition in self.canon_traditions, \
          "Tradition '{}' must be one of {}".format(tradition, self.canon_traditions)
        return tradition in self.canons


_BookGroups = [
    BookGroup("Pentateuch",
              ['Ge', 'Ex', 'Le', 'Nu', 'Dt']),
    BookGroup("OT History",
              ['Jos', 'Jdg', 'Ru', '1 Sa', '2 Sa', '1 Ki', '2 Ki', '1 Ch', '2 Ch',
               'Ezr', 'Ne', 'Es']),
    BookGroup("Poetry",
              ['Job', 'Ps', 'Pr', 'Ec', 'So', 'La']),
    BookGroup("Major Prophets",
              ['Is', 'Je', 'Eze']),
    BookGroup("Minor Prophets",
              ['Da', 'Ho', 'Joe', 'Am', 'Obad', 'Jon', 'Mic', 'Na', 'Hab', 'Zep', 'Hag', 'Zec', 'Mal']),
    BookGroup("Apocrypha",
              ['Tob', 'Jdt', 'Add Es', 'Wis', 'Sir', 'Bar', 'LJe', 'Song Thr', 'Sus', 'Bel',
               '1 Mac', '2 Mac', '1 Esd', 'PrMan', 'AddPs', '3 Mac', '2 Esd', '4 Mac',
              'Ode', 'PsSol', 'EpLaod']),
    BookGroup("Gospels",
              ['Mt', 'Mk', 'Lk', 'Jn']),
    BookGroup("NT History",
              ['Ac']),
    BookGroup("Pauline Epistles",
              ['Ro', '1 Co', '2 Co', 'Ga', 'Eph', 'Php', 'Col', '1 Th', '2 Th',
               '1 Ti', '2 Ti', 'Tit', 'Phm']),
    BookGroup("Pastoral Epistles",
              ['1 Ti', '2 Ti', 'Tit', 'Phm'],
              # ['Pauline Epistles']
    ),
    BookGroup("Catholic Epistles",
              ['Heb', 'Jas', '1 Pe', '2 Pe', '1 Jn', '2 Jn', '3 Jn', 'Jud']),
    BookGroup("Apocalypse",
              ['Re']),
    ]

# register in groupnames
# for group, books, supergroups in _BookGroups:
for group in _BookGroups:
    name = getattr(group, 'name')
    if name in groupnames:
        warn("Overwriting groupnames[{}] with {}".format(name, group))
    else:
        groupnames[name] = group
