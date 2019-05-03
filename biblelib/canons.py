"""Canon traditions for Bible books


"""

from collections import namedtuple

Canon = namedtuple('Canon', ['name', 'books'])

catholic_canon = Canon('Catholic', [])
jewish_canon = Canon('Jewish', [])
protestant_canon = Canon('Protestant', [])
ethiopian_canon = Canon('Ethiopian', [])
orthodox_canon = Canon('Orthodox', [])
samaritan_canon = Canon('Samaritan', [])
syriac_canon = Canon('Syriac', [])
    
