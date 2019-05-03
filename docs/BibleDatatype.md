# The Logos Bible Datatype

* The serialized form of an atomic bible datatype reference is
  `{bibledatatype}.{book}.{chapter}.{verse}`. For example
  `bible.64.3.16` represents John 3:16. 
    * In this atomic form, the
      bibledatatype and book are required, while chapter and verse are
      both optional. 
    * The default bibletype is `bible`.
* In range references, the book, chapter, and verse (if specified) are
  made explicit for both the startpoint and endpoint. So the
  datatype representation for Mark 4:1-9 is `bible.62.4.1-62.4.9`. 
* Bible books are numbered starting with Genesis as `index = 1`, included
  deuterocanonical books in sequence between Hebrew Bible and New
  Testament. Consequently, the Gospel of Matthew has `index = 61` (not
  40, even though it is the 40th book in the Protestant Canon). The
  full list can be found at [Logos Bible Book
  Names](https://wiki.logos.com/Logos_Bible_Book_Names). 

## Implementation in `biblelib`

* `biblelib` implements the following reference types:
    * `Bookref`: a reference to a Bible book, with no chapter
      specification. 
    * `Chapterref`: a reference to a chapter in a book, with no verse
      specification. 
    * `Verseref`: a reference to book, chapter, and verse.
    * `RangeChapterref`: a reference to a range whose start and end
      are both chapters, with no verse specification, e.g. Is 1-39
      (whose datatype serialization is `bible.23.1-23.39`)
    * `RangeVerseref`: a reference to a range whose start and end both
      specify verses, e.g. Mark 4:1-9 (represented as `bible.62.4.1-62.4.9`) 
* Only a small number of Bible data types are supported (see
  `biblelib.reference.BIBLE_DATATYPES`). While Logos software has
  extensive support for mapping difference verse schemes ("verse
  maps"), that support is not included in this library.
* While the Logos Bible Datatype supports book ranges (`bible.1-5` is
  a valid reference to the five books of the Penteteuch), `biblelib`
  does not. 

See the [Logos Bible Datatype](https://wiki.logos.com/bible_datatypes)
on the Logos Software Wiki for additional information.
