# -*- coding: utf-8 -*-
# Version: 2.4
# See github page to report issues or contribute:
# https://github.com/hssm/anki-ignore-accents

import shlex

from aqt import gui_hooks
from aqt.browser import SearchContext


def willSearch(ctx: SearchContext):
    terms = shlex.split(ctx.search, posix=False)
    c_terms = []
    # Recombine quoted terms that were split on spaces
    # E.g: deck:"my deck" becomes |deck:"my|, |deck"|
    for i, t in enumerate(terms):
        while t.count('"') == 1 and i < len(terms)-1:
            t = t + ' ' + terms[i+1]
            del terms[i+1]
        terms[i] = t

    ctx.search = ' '.join(solveTerm(t) for t in terms)
    #print(ctx.search)

def solveTerm(term):
    # Ignore anything with : as they are search features in anki
    # If we encounter minus, quotes or brackets, move on to next letter. We want to preserve
    # negation and/or grouping and only modify the terms inside them. This technique works well.
    # Ignore "or" and "and" as they are also anki search keywords

    if ':' in term:
        return term
    if term[0] in ["'", '"', '-', '(', ')']:
        if len(term) > 1:
            return term[0] + solveTerm(term[1:])
        return term
    if term == 'or' or term == 'and':
        return term
    return 'nc:' + term

gui_hooks.browser_will_search.append(willSearch)