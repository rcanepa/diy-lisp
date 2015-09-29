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
    # Handle lists
    # if 'reverse' in env.bindings:
    #     print ast, env
    if is_list(ast):

        if len(ast) == 0:
            raise LispError('calling nothing is not allowed')

        if is_closure(ast[0]):
            if len(ast[1:]) != len(ast[0].params):
                raise LispError('wrong number of arguments, expected %d got %d' % (len(ast[0].params), len(ast[1:])))
            # Set parameters to the closure's environment
            variables = dict()
            for idx, param in enumerate(ast[1:]):
                variables[ast[0].params[idx]] = evaluate(param, env)
            call_env = ast[0].env.extend(variables)
            print("Evaluating:", ast, call_env)
            return evaluate(ast[0].body, call_env)

        elif ast[0] == "cons":
            lst = list()
            lst.append(evaluate(ast[1], env))
            lst += evaluate(ast[2], env)
            return lst

        elif ast[0] in ["head", "tail"]:
            lst = evaluate(ast[1], env)
            if not is_list(lst):
                raise LispError('can\'t apply %s on something different than a list' % ast[0])
            if len(lst) == 0:
                raise LispError('can\'t apply %s on an empty list' % ast[0])
            else:
                return lst[0] if ast[0] == "head" else lst[1:]

        elif ast[0] == "empty":
            lst = evaluate(ast[1], env)
            if not is_list(lst):
                raise LispError('can\'t apply %s on something different than a list' % ast[0])
            return True if len(lst) == 0 else False

        elif ast[0] == "if":
            return evaluate(ast[2], env) if evaluate(ast[1], env) else evaluate(ast[3], env)

        elif ast[0] == "quote":
            return ast[1]

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

        elif ast[0] == "lambda":
            if len(ast) != 3:
                raise LispError("number of arguments")
            if not is_list(ast[1]):
                raise LispError("Parameters should be a list, and you gave %s" % ast[1])
            return Closure(env, ast[1], ast[2])

        elif ast[0] == "eq":
            # left and right sides of the equality test
            left = evaluate(ast[1], env)
            right = evaluate(ast[2], env)
            # list are always different (by definition)
            return False if is_list(left) or is_list(right) else left == right

        elif type(ast[0]) is str and ast[0] in ["+", "-", "/", "*", "mod", ">", "<", "<=", ">="]:
            # left and right side operands of the math operation
            left = evaluate(ast[1], env)
            right = evaluate(ast[2], env)
            if type(left) is str or type(right) is str:  # math operations on integers only
                raise LispError("One of the arguments is not a number: %s %s" % (left, right))
            evaluation = eval(str(left) + ast[0].replace("mod", "%") + str(right))
            return evaluation

        else:
            symbol = evaluate(ast[0], env)
            if is_closure(symbol):
                ast[0] = symbol
                return evaluate(ast, env)
            raise LispError('not a function')

    # Handle atoms
    else:
        if is_boolean(ast) or is_integer(ast):
            return ast
        elif type(ast) is str:
            # Check for closure and evaluate it
            return env.lookup(ast)
        else:
            raise LispError("Unrecognized type %s" % ast)
