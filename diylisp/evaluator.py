# -*- coding: utf-8 -*-

from .types import Environment, LispError, Closure, String
from .ast import is_boolean, is_atom, is_symbol, is_list, is_closure, is_integer, is_string
from .asserts import assert_exp_length, assert_valid_definition, assert_boolean
from .parser import unparse

"""
This is the Evaluator module. The `evaluate` function below is the heart
of your language, and the focus for most of parts 2 through 6.

A score of useful functions is provided for you, as per the above imports, 
making your work a bit easier. (We're supposed to get through this thing 
in a day, after all.)
"""

def evaluate(ast, env):
    """Evaluate an Abstract Syntax Tree in the specified environment."""

    if is_list(ast):
        form = ast[0]
        if form == "quote":
            return eval_quote(ast, env)
        if form == "atom":
            return eval_atom(ast, env)
        if form == "eq":
            return eval_eq(ast, env)
        if is_math(form):
            return eval_math(ast, env)
        if form == "if":
            return eval_if(ast, env)

    return ast

def eval_quote(ast, env):
    return ast[1]

def eval_atom(ast, env):
    arg = evaluate(ast[1], env)
    return is_atom(arg)

def eval_eq(ast, env):
    arg1 = evaluate(ast[1], env)
    arg2 = evaluate(ast[2], env)
    return is_atom(arg1) and arg1 == arg2

math = {
    "+": lambda x, y: x + y,
    "-": lambda x, y: x - y,
    "/": lambda x, y: x / y,
    "*": lambda x, y: x * y,
    "mod": lambda x, y: x % y,
    ">": lambda x, y: x > y
}

def is_math(form):
    return form in math.keys()

def eval_math(ast, env):
    op   = ast[0]
    arg1 = evaluate(ast[1], env)
    arg2 = evaluate(ast[2], env)

    if not is_integer(arg1) or not is_integer(arg2):
        raise LispError("Illegal argument: Non-numeric argument to `{}`".format(op))

    return math[op](arg1, arg2)

def eval_if(ast, env):
    pred = evaluate(ast[1], env)

    if pred:
        return evaluate(ast[2], env)
    else:
        return evaluate(ast[3], env)

