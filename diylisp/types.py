# -*- coding: utf-8 -*-

"""
This module holds some types we'll have use for along the way.

It's your job to implement the Closure and Environment types.
The LispError class you can have for free :)
"""


class LispError(Exception):
    """General lisp error class."""
    pass


class Closure:
    def __init__(self, env, params, body):
        raise NotImplementedError("DIY")

    def __repr__(self):
        return "<closure/%d>" % len(self.params)


class Environment:
    def __init__(self, variables=None):
        self.bindings = variables if variables else {}

    def lookup(self, symbol):
        var = self.bindings.get(symbol, None)
        if var:
            return var
        raise LispError('Variable %s is not defined.' % symbol)

    def extend(self, variables):
        extended = dict(self.bindings)
        extended.update(variables)
        return Environment(extended)

    def set(self, symbol, value):
        if symbol in self.bindings:
            raise LispError('Variable %s already defined.' % symbol)
        self.bindings[symbol] = value


class String:
    """
    Simple data object for representing Lisp strings.

    Ignore this until you start working on part 8.
    """

    def __init__(self, val=""):
        self.val = val

    def __str__(self):
        return '"{}"'.format(self.val)

    def __eq__(self, other):
        return isinstance(other, String) and other.val == self.val
