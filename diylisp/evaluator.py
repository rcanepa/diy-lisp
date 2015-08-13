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

    if is_symbol(ast):
        return env.lookup(ast)

    if is_list(ast):
        form = get_form(ast)

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
        if form == "define":
            return eval_define(ast, env)
        if form == "lambda":
            return eval_lambda(ast, env)
        if form == "cons":
            return eval_cons(ast, env)
        if form == "head":
            return eval_head(ast, env)
        if form == "tail":
            return eval_tail(ast, env)
        if form == "empty":
            return eval_empty(ast, env)
        if form == "cond":
            return eval_cond(ast, env)
        if form == "let":
            return eval_let(ast, env)
        if form == "defn":
            return eval_defn(ast, env)
        else:
            return call(ast, env)

    return ast

def get_form(ast):
    if len(ast) == 0:
        raise LispError("Call to empty list")
    return ast[0]

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

def eval_define(ast, env):
    if len(ast) != 3:
        raise LispError("Wrong number of arguments to define statment: `{}`".format(unparse(ast)))

    name = ast[1]
    if not is_symbol(name):
        raise LispError("Defined variable on non-symbol: `{}`".format(unparse(name)))

    env.set(name, evaluate(ast[2], env))
    return name


def eval_lambda(ast, env):
    params = ast[1]

    if not is_list(params):
        raise LispError("First argument to `lambda` should be a list, got `{}`".format(unparse(params)))

    if len(ast) != 3:
        raise LispError("Wrong number of arguments to `lambda`: {}".format(len(ast)))

    body = ast[2]

    return Closure(env, params, body)

def apply_fn(ast, env):
    closure = ast[0]
    args = [evaluate(exp, env) for exp in ast[1:]]

    if len(args) != len(closure.params):
        msg = "Got wrong number of arguments, expected {} got {}"
        raise LispError(msg.format(len(closure.params), len(args)))

    bound_arguments = dict(zip(closure.params, args))
    call_env = closure.env.extend(bound_arguments)

    return evaluate(closure.body, call_env)

def call(ast, env):
    form = ast[0]

    if is_closure(form):
        return apply_fn(ast, env)
    if is_symbol(form) or is_list(form):
        return evaluate([evaluate(form, env)] + ast[1:], env)
    else:
        raise LispError("Illegal function call: not a function: `{}`".format(unparse(ast)))

def eval_cons(ast, env):
    head = evaluate(ast[1], env)
    tail = evaluate(ast[2], env)

    if is_string(head) and is_string(tail):
        return String(head.val + tail.val)

    return [head] + tail

def eval_head(ast, env):
    lst = evaluate(ast[1], env)

    if is_string(lst):
        return String(lst.val[0])

    if not is_list(lst):
        raise LispError("Cannot get `head` from non-list")

    if len(lst) == 0:
        raise LispError("Head of empty list")

    return lst[0]

def eval_tail(ast, env):
    lst = evaluate(ast[1], env)

    if is_string(lst):
        return String(lst.val[1:])

    if not is_list(lst):
        raise LispError("Cannot get `tail` from non-list")

    if len(lst) == 0:
        raise LispError("Tail of empty list")

    return lst[1:]

def eval_empty(ast, env):
    lst = evaluate(ast[1], env)

    if is_string(lst):
        return lst.val == ""

    if not is_list(lst):
        raise LispError("Cannot check `empty` on non-list")

    return len(lst) == 0

def eval_cond(ast, env):
    for cond, then in ast[1]:
        if evaluate(cond, env):
            return evaluate(then, env)

    return False

def eval_let(ast, env):
    bindings = ast[1]
    body = ast[2]
    for symbol, expression in bindings:
        env = env.extend({symbol: evaluate(expression, env)})

    return evaluate(body, env)

def eval_defn(ast, env):
    name = ast[1]
    params = ast[2]
    body = ast[3]

    env.set(name, Closure(env, params, body))
    return name
