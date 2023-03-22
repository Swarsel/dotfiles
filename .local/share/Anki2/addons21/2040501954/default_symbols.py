""" 
This file contains the default symbol list as well as a list of special symbols
which should behave like colon-delimited symbols.
"""
import itertools
from collections import OrderedDict

SPECIAL_KEYS = [
    '->',
    '<-',
    '=>',
    '<=',
]

""" Symbols Key-Value Pair Definitions """

_ARROWS = [
    ('->',          u'\u2192'),
    ('=>',          u'\u21D2'),
    ('<-',          u'\u2190'),
    ('<=',          u'\u21D0'),
    (':N:',         u'\u2191'),
    (':N2:',        u'\u21D1'),
    (':S:',         u'\u2193'),
    (':S2:',        u'\u21D3'),
    (':E:',         u'\u2192'),
    (':E2:',        u'\u21D2'),
    (':W:',         u'\u2190'),
    (':W2:',        u'\u21D0'),
]

_TYPOGRAPHY = [
    ('--',          u'\u2012'),
    ('---',         u'\u2014'),
    (':dagger:',    u'\u2020'),
    (':ddagger:',   u'\u2021'),
    (':section:',   u'\u00A7'),
    (':paragraph:', u'\u00B6'),
]

_MATH_GEN = [
    (':infty:',     u'\u221E'),
    (':deg:',       u'\u00B0'),
    (':permil:',    u'\u2030'),
    (':sqrt:',      u'\u221A'),
    (':cubert:',    u'\u221B'),
    (':4thrt:',     u'\u221C'),
    (':angle:',     u'\u2220'),
    (':hbar:',      u'\u210F'),
]

_MATH_BINARY = [
    (':pm:',        u'\u00B1'),
    (':mp:',        u'\u2213'),
    (':dot:',       u'\u00B7'),
    (':times:',     u'\u00D7'),
    (':div:',       u'\u00F7'),
]

_MATH_RELATION = [
    (':approx:',    u'\u2248'),
    (':equiv:',     u'\u2261'),
    (':propto:',    u'\u221D'),
    (':neq:',       u'\u2260'),
    (':geq:',       u'\u2265'),
    (':leq:',       u'\u2264'),
    (':>>:',        u'\u226B'),
    (':<<:',        u'\u226A'),
]

_MATH_SETS = [
    (':subset:',    u'\u2282'),
    (':subseteq:',  u'\u2286'),
    (':supset:',    u'\u2283'),
    (':supseteq:',  u'\u2287'),
    (':in:',        u'\u2208'),
    (':ni:',        u'\u220B'),
    (':cap:',       u'\u2229'),
    (':cup:',       u'\u222A'),
    (':emptyset:',  u'\u2205'),
]

_MATH_LOGIC = [
    (':neg:',       u'\u00AC'),
    (':vee:',       u'\u2228'),
    (':wedge:',     u'\u2227'),
    (':forall:',    u'\u2200'),
    (':exists:',    u'\u2203'),
    (':therefore:', u'\u2234'),
]

_MATH_CALCULUS = [
    (':nabla:',     u'\u2207'),
    (':partial:',   u'\u2202'),
    (':integral:',  u'\u222B'),
]

_FRACTIONS = [
    (':1/2:',       u'\u00BD'),
    (':1/3:',       u'\u2153'),
    (':2/3:',       u'\u2154'),
    (':1/4:',       u'\u00BC'),
    (':3/4:',       u'\u00BE'),
    (':1/5:',       u'\u2155'),
    (':2/5:',       u'\u2156'),
    (':3/5:',       u'\u2157'),
    (':4/5:',       u'\u2158'),
    (':1/6:',       u'\u2159'),
    (':5/6:',       u'\u215A'),
    (':1/7:',       u'\u2150'),
    (':1/8:',       u'\u215B'),
    (':3/8:',       u'\u215C'),
    (':5/8:',       u'\u215D'),
    (':7/8:',       u'\u215E'),
    (':1/9:',       u'\u2151'),
    (':1/10:',      u'\u2152'),
]

_GREEK_LOWER = [
    (':alpha:',     u'\u03B1'),
    (':beta:',      u'\u03B2'),
    (':gamma:',     u'\u03B3'),
    (':delta:',     u'\u03B4'),
    (':epsilon:',   u'\u03B5'),
    (':zeta:',      u'\u03B6'),
    (':eta:',       u'\u03B7'),
    (':theta:',     u'\u03B8'),
    (':iota:',      u'\u03B9'),
    (':kappa:',     u'\u03BA'),
    (':lambda:',    u'\u03BB'),
    (':mu:',        u'\u03BC'),
    (':nu:',        u'\u03BD'),
    (':xi:',        u'\u03BE'),
    (':omicron:',   u'\u03BF'),
    (':pi:',        u'\u03C0'),
    (':rho:',       u'\u03C1'),
    (':sigma:',     u'\u03C3'),
    (':tau:',       u'\u03C4'),
    (':upsilon:',   u'\u03C5'),
    (':phi:',       u'\u03C6'),
    (':chi:',       u'\u03C7'),
    (':psi:',       u'\u03C8'),
    (':omega:',     u'\u03C9'),
]

_GREEK_UPPER = [
    (':Alpha:',     u'\u0391'),
    (':Beta:',      u'\u0392'),
    (':Gamma:',     u'\u0393'),
    (':Delta:',     u'\u0394'),
    (':Epsilon:',   u'\u0395'),
    (':Zeta:',      u'\u0396'),
    (':Eta:',       u'\u0397'),
    (':Theta:',     u'\u0398'),
    (':Iota:',      u'\u0399'),
    (':Kappa:',     u'\u039A'),
    (':Lambda:',    u'\u039B'),
    (':Mu:',        u'\u039C'),
    (':Nu:',        u'\u039D'),
    (':Xi:',        u'\u039E'),
    (':Omicron:',   u'\u039F'),
    (':Pi:',        u'\u03A0'),
    (':Rho:',       u'\u03A1'),
    (':Sigma:',     u'\u03A3'),
    (':Tau:',       u'\u03A4'),
    (':Upsilon:',   u'\u03A5'),
    (':Phi:',       u'\u03A6'),
    (':Chi:',       u'\u03A7'),
    (':Psi:',       u'\u03A8'),
    (':Omega:',     u'\u03A9'),
]

_CURRENCY = [
    (':cent:',      u'\u00A2'),
    (':pound:',     u'\u00A3'),
    (':euro:',      u'\u20AC'),
    (':lira:',      u'\u20A4'),
    (':peso:',      u'\u20B1'),
    (':ruble:',     u'\u20BD'),
    (':rupee:',     u'\u20B9'),
    (':won:',       u'\u20A9'),
    (':yen:',       u'\u00A5'),
    (':yuan:',      u'\u00A5'),
]


""" Create Index of Keys and Default List """

_SYMBOL_DICT = OrderedDict([
    ("Arrows", _ARROWS),
    ("Typography", _TYPOGRAPHY),
    ("Math (General)", _MATH_GEN),
    ("Math (Binary Operators)", _MATH_BINARY),
    ("Math (Relational)", _MATH_RELATION),
    ("Math (Sets)", _MATH_SETS),
    ("Math (Logical)", _MATH_LOGIC),
    ("Math (Calculus)", _MATH_CALCULUS),
    ("Fractions", _FRACTIONS),
    ("Greek Symbols (Lowercase)", _GREEK_LOWER),
    ("Greek Symbols (Uppercase)", _GREEK_UPPER),
    ("Currency", _CURRENCY),
])

DEFAULT_MATCHES = list(itertools.chain.from_iterable(_SYMBOL_DICT.values()))
