# -*- encoding: utf-8 -*-
from functools import wraps

def get_symbol(f):
    @wraps(f)
    def wrapper(self, edit):
        view = self.view
        region = view.sel()[0]
        if region.begin() == region.end():
            region = view.word(region)
        symbol = view.substr(region)

        return f(self, edit, view, symbol)
    return wrapper
