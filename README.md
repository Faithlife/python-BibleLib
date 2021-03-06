# BibleLib
========================

This repository provides utilities for working with data about 

* Bible books and groupings
* a "standard" set of pericope definitions
* Bible references

This does *not* include any actual Bible texts: for that purpose, see
the [Biblia.com API](http://bibliaapi.com/docs/) developed by
[Faithlife](https://faithlife.com/about). There is a simple Biblia
client in Python in the `biblia` package.


## To Do

- Tests via ``$ setup.py test`` (if it's concise).

Pull requests are encouraged!

## Limitations

This supports the conventions of the [Logos Bible
Datatype](https://wiki.logos.com/bible_datatypes), but much of this
functionality should be useful for other purposes as well. Note that
only a small number of the most common Bible datatypes are supported,
and full support is never likely to be added (we have much existing C#
code in the app to handle that).

## License

This software is Copyright 2018 Faithlife Corporation, and distributed
under the MIT License.

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

