"""Utilities for working with Bible data"""

from .books import Book
from .groups import BookGroup
from .core import makeBiblerefFromDTR
#from .pericopes
#from .biblia


__version__ = "0.5"
__title__ = "biblelib"
__description__ = "Manage Bible references and metadata"
__uri__ = "http://github.com/Faithlife/Biblelib"
__doc__ = __description__ + " <" + __uri__ + ">"

__author__ = "Sean Boisen"
__email__ = "sean@logos.com"

__license__ = "MIT"
__copyright__ = "Copyright (c) 2018 Faithlife Corporation"


# __all__ = ['BiblelibError', 'ReferenceValidationError',
#            'HUMAN_BIBLE_DATATYPES', 'BIBLE_DATATYPES', 'makeBiblerefFromDTR']




