"""Client for api.biblia.com.

You need your own API key, and you'll do better if you've read the
docs at http://api.biblia.com/docs.

Example usage::

>>> from biblelib.biblia import client
>>> api = client.API(key)
>>> api.tag(text='Does Mark 4:9 occur in here??')
u'{"text":"Does <a href=\\"http://ref.ly/Mark4.9\\">Mark 4:9</a> occur in here??"}'
# tag and return Markdown format with Logos URL
>>> api.tag(text="See Mark 4:1-9 and following.", tagFormat='[{text}](https://ref.ly/logosref/bible.{query})')
{'text': 'See [Mark 4:1-9](https://ref.ly/logosref/bible.Mark4.1–9) and following.'}


# get the LEB text of Mark 4:9
>>> bib.content(bible='LEB', passage='Mark 4:9')
u'And he said, \u201cWhoever has ears to hear, let him hear!\u201d'
# get a list of all the Bible IDs
>>> [x.get('bible') for x in bib.find()]
['DARBY', 'ASV', 'ARVANDYKE', 'BYZ', 'LEB', ...]
# identify and hyperlink references in a string
>>> bib.tag(text='Does Mark 4:9 occur in here??')
u'{"text":"Does <a href=\\"http://ref.ly/Mark4.9\\">Mark 4:9</a> occur in here??"}'

"""

# Version: 0.4
# Author: Sean Boisen
# Copyright: Copyright (C) 2010 Logos Bible Software
# License: Public Domain

from collections import namedtuple
import json
import requests
# import urllib
# import urllib2


__all__ = ('API')


# ToDo:


class API(object):
    """Encapsulates Biblia API functionality. 

    Caching assumes JSON data, so some API options aren't supported: 
    YMMV.

    """
    # includes the API version information
    base = "https://api.biblia.com/v1/bible"
    # cache results for efficiency
    _cache = {}
    
    def __init__(self, api_key, format='txt'):
        """Construct a new BibliaAPI instance for a given API key.
        
        api_key: The API key as obtained from Biblia.
        format: The format for Bible content. Use either "txt" for plain text, or "html". 
        """
        self.api_key = api_key
        assert format in ['txt', 'html'], f'Invalid format: {format}'
        self.default_format = format
        
    def content(self, bible='LEB.html.json', **kwargs):
        """Scan TEXT which is presumed to be a Bible reference, rendering
        the result with STYLE.
        """
        # more options and testing required here
        assert bible, 'content: bible is required'
        assert bible.endswith(".json"), "content: JSON results are required for caching"
        assert kwargs.get('passage'), 'content: passage is required'
        # different options for a return value if .html
        return self._biblia_get(form=f'content/{bible}', args=kwargs)

    def parse(self, **kwargs):
        """Scan TEXT which is presumed to be a Bible reference, rendering
        the result with STYLE.
        """
        assert kwargs.get('passage'), 'parse: passage is required'
        return self._biblia_get(form='parse', args=kwargs)

    def scan(self, **kwargs):
        """Scan text and return locations of Bible references. """
        assert kwargs.get('text'), f'scan: text attribute must be supplied'
        return self._biblia_get(form='scan', args=kwargs)

    def tag(self, **kwargs):
        """Tag TEXT or the text at URL with Bible references. 

        Only one is allowed. Tags go to http://ref.ly by default. 

        Use this tagFormat to get a Markdown result with a ref.ly URL:
        '[{text}](https://ref.ly/logosref/bible.{query})'
        """
        assert not(kwargs.get('text') and kwargs.get('url')), \
            'tag: Only one of text and url is allowed'
        assert kwargs.get('text') or kwargs.get('url'), \
            'tag: Either text or url is required'
        return self._biblia_get(form='tag', args=kwargs)

    def tag_markdown(self, **kwargs):
        assert 'tagFormat' not in kwargs, \
            'tag_markdown: incompatible tagFormat {}'.format(kwargs.get('tagFormat'))
        return self.tag(tagFormat='[{text}](https://ref.ly/logosref/bible.{query})', **kwargs)

    def _biblia_get(self, form, args):
        """FORM is the URL fragment for a recognize service. ARGS are a dict
        of the appropriate arguments for that service. No checking
        here: just assemble, fire, and return the results under
        RESULTKEY (which is also service-specific).

        """
        baseurl = f'{self.base}/{form}'
        # tuple-ify so it can be hashed for the cache
        argstuple = tuple(args.items())
        if argstuple not in self._cache:
            args.update(key=self.api_key)
            response = requests.get(baseurl, params=args)
            if response.status_code == 200:
                self._cache[argstuple] = response.json()
            else:
                response.raise_for_status()
        return self._cache[argstuple]
