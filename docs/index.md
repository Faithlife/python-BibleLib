# BibleLib Documentation

This repository provides utilities for working with Bible books and references.

## Design Goals

* Provide a Pythonic representation of Bible references (`Bibleref`). 
* Provide methods for retrieving information about the canonical
  books of the Bible, their abbreviated names, and their chapters and
  verses.
* Provide basic support for groups of Bible books (Pentateuch,
  Poetry, Pastoral Epistles, etc.) and canons (Jewish, Catholic,
  Protestant). 
* Provide an alternate indexing scheme (`vindex`) for indexing verse
  references within a book.
* Define a standard set of pericopes for Bible passages. 
* Parse human-readable references into `Bibleref` objects, and
  serialize `Bibleref` objects. 
* Provide a simple client for the Biblia API.

