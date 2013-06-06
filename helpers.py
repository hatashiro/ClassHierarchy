# -*- encoding: utf-8 -*-
import re
from functools import wraps

def hierarchy_base_decorator(f):
    @wraps(f)
    def wrapper(self, edit, **args):
        view = self.view

        if not args.get('no_symbol'):
            symbol = args.get('symbol')
            if not symbol:
                region = view.sel()[0]
                if region.begin() == region.end():
                    region = view.word(region)
                symbol = view.substr(region)
        else:
            symbol = None

        window = args.get('window')
        if not window:
            window = None

        return f(self, edit, view, symbol, window)
    return wrapper

def to_underscore(camelcase):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', camelcase)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
