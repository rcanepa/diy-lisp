# -*- coding: utf-8 -*-

from .types import Environment, LispError, Closure, String
from .ast import is_boolean, is_atom, is_symbol, is_list, is_closure, is_integer, is_string
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
    print ast, env
    if is_atom(ast) or (is_list(ast) and len(ast) <= 1):
        if type(ast) is str:
            return env.lookup(ast)
        return ast
    else:  # it should be a list
        if ast[0] == "if":
            if evaluate(ast[1], env) is True:
                return evaluate(ast[2], env)
            else:
                return evaluate(ast[3], env)
        elif ast[0] == "quote":
            return evaluate(ast[1], env)
        elif ast[0] == "atom":
            return is_atom(evaluate(ast[1], env))
        elif ast[0] == "define":
            # Validate the number of arguments
            if len(ast) != 3:
                raise LispError('Wrong number of arguments. You must pass 2 of them (the variable name and its value).')
            # Be sure that the variable name is a symbol (not a number or a boolean)
            if is_symbol(ast[1]):
                value = evaluate(ast[2], env)
                env.set(ast[1], value)
            else:
                raise LispError('non-symbol')
        elif ast[0] == "eq":
            # left and right sides of the equality test
            left = evaluate(ast[1], env)
            right = evaluate(ast[2], env)
            # list are always different (by definition)
            if is_list(left) or is_list(right):
                return False
            else:
                return left == right
        elif type(ast[0]) is str and ast[0] in ["+", "-", "/", "*", "mod", ">", "<"]:
            # left and right side operands of the math operation
            left = evaluate(ast[1], env)
            right = evaluate(ast[2], env)
            if type(left) is str or type(right) is str:  # math operations on integers only
                raise LispError("One of the arguments is not a number: %s %s" % (left, right))
            evaluation = eval(str(left) + ast[0].replace("mod", "%") + str(right))
            return evaluation
        else:
            return env.lookup(ast[0])
            # return ast
