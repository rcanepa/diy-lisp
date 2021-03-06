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
        self.env = env if env else Environment()
        self.params = params if params else []
        self.body = body if body else []

    def __repr__(self):
        return "<closure/%s>" % self.params


class Environment:

    def __init__(self, variables=None):
        self.bindings = variables if variables else {}

    def lookup(self, symbol):
        var = self.bindings.get(symbol, None)

        if var is not None:
            return var

        raise LispError('Variable %s is not defined.' % symbol)

    def extend(self, variables=None):
        extended = self.bindings.copy()
        extended.update(variables) if variables else extended.update({})
        return Environment(extended)

    def set(self, symbol, value):
        if symbol in self.bindings:
            raise LispError('Variable %s already defined.' % symbol)

        self.bindings[symbol] = value

    def __repr__(self):
        return "<environment: %s>" % self.bindings


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

    def __len__(self):
        return len(self.val)

    def __getitem__(self, item):
        return self.val[item]

    def __add__(self, other):
        if type(other) == str:
            return String(self.val + other)

        if type(other) == String:
            return String(self.val + str(other))

        raise TypeError("unsupported operand type(s) for +: 'String' and '{}'".format(type(other)))
