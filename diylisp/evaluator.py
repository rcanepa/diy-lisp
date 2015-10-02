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
    """
    Evaluate ast (Abstract Syntax Tree) in the Environment provided by env.
    :param ast: list or atom
    :param env: AST Environment
    :return:    the result of the evaluation
    """

    exptype = expression_type(ast)

    if exptype == "list":

        form = ast[0]

        if len(ast) == 0:
            raise LispError('Calling statement without arguments is not allowed.')

        if is_closure(form):
            return eval_closure(ast, env)

        if form == "quote":
            return eval_quote(ast)

        if form == "atom":
            return eval_atom(ast, env)

        if form == "eq":
            return eval_eq(ast, env)

        if form == "if":
            return eval_if(ast, env)

        if form == "cond":
            return eval_cond(ast, env)

        if form == "define":
            return eval_define(ast, env)

        if form == "defn":
            return eval_defn(ast, env)

        if form == "lambda":
            return eval_lambda(ast, env)

        if form == "let":
            return eval_let(ast, env)

        if form == "cons":
            return eval_cons(ast, env)

        if form == "empty":
            return eval_empty(ast, env)

        if form == "head":
            return eval_head(ast, env)

        if form == "tail":
            return eval_tail(ast, env)

        if type(form) is str and form in ["+", "-", "/", "*", "mod", ">", "<", "<=", ">="]:
            return eval_math(ast, env)

        symbol = evaluate(ast[0], env)

        if is_closure(symbol):
            ast[0] = symbol
            return evaluate(ast, env)

        raise LispError('Not a function {}.'.format(symbol))

    else:

        if exptype == "number" or exptype == "boolean" or exptype == "string":
            return ast

        else:
            return env.lookup(ast)


def expression_type(exp):
    """
    Consume a type of expression and return a string with the name of the type.
    :param exp: list | number | boolean | symbol | closure
    :return:    string
    """
    if is_list(exp):
        return "list"

    else:
        if is_integer(exp):
            return "number"

        if is_boolean(exp):
            return "boolean"

        if is_closure(exp):
            return "closure"

        if is_symbol(exp):
            return "symbol"

        if is_string(exp):
            return "string"

        else:
            raise LispError("Unrecognized type {}.".format(exp))


def eval_atom(ast, env):
    """
    Consume a list with its first element equal to "atom" and return true
    if the second element is an atom.
    E.g.: ["atom", [1, 2, 3]] -> False
    :param ast: ["atom", expr]
    :param env: AST Environment
    :return:    bool
    """
    return is_atom(evaluate(ast[1], env))


def eval_eq(ast, env):
    """
    Consume a list with first element equal to "eq" and two arguments. If the arguments are equal
    it return True. Two list are always NOT equal.
    E.g.: ["eq", 3, 4] -> False
    :param ast: ["eq", expr1, expr2]
    :param env: AST Environment
    :return:    bool
    """
    expr1 = evaluate(ast[1], env)
    expr2 = evaluate(ast[2], env)
    return False if is_list(expr1) or is_list(expr2) else expr1 == expr2


def eval_define(ast, env):
    """
    Consume a list with a define expression and set a new variable / value in the Environment (env)
    E.g.: ["define", "foo", "bar"] -> env.bindings.foo = "bar"
    :param ast: ["define", symbol, expr]
    :param env: AST Environment (the value will be defined here)
    :return:    the variable name
    """
    if len(ast) != 3:
        raise LispError('Wrong number of arguments. You must pass 2 of them (the variable name and its value).')

    name = ast[1]

    if is_symbol(name):
        value = evaluate(ast[2], env)
        env.set(name, value)
        return name

    else:
        raise LispError('The name of the variable is not a symbol.')


def eval_defn(ast, env):
    """
    Consume a list with a "defn" expression and creates a closure that will be assigned to an
    environment variable.
    E.g.: ["defn", "foo", ["x", "y"], ["+", "x", "y"]] -> foo: Closure
    :param ast: ["defn", string, [], []]
    :param env: AST Environment
    :return:    the name of the function
    """
    fname = ast[1]
    closure = eval_lambda(ast[1:], env)
    env.set(fname, closure)
    return fname


def eval_lambda(ast, env):
    """
    Consume a list with a lambda expression and produce a Closure with the parameters and body
    contained in the list.
    E.g.: ["lambda", ["a", "b"], ["+", "a", "b"]] -> Closure
    :param ast: ["lambda", [], expr]
    :param env: AST Environment
    :return:    Closure
    """
    if len(ast) != 3:
        raise LispError("A lambda expression requires 3 arguments and received {}".format(len(ast)))

    if not is_list(ast[1]):
        raise LispError("Parameters should be a list, and you gave {}".format(ast[1]))

    return Closure(env, ast[1], ast[2])


def eval_let(ast, env):
    """
    Consume a list with 3 elements. The first one is the string "let" and the rest must be lists. The
    first list contains the local binding definitions, and the second list the expression with access to
    those bindings.
    E.g.: ["let", [["a", ["+", 100, 20]]], ["+", "a", 5]] -> 125
    :param ast: ["let", [], []]
    :param env: AST Environment
    :return:    result from the expression evaluation
    """
    bindings = ast[1]

    let_env = env.extend({})
    for key, val in bindings:
        let_env = let_env.extend({key: evaluate(val, let_env)})

    return evaluate(ast[2], let_env)


def eval_closure(ast, env):
    """
    Consume a list with a closure expression.
    :param ast: [Closure, param1, param2, ..., paramN]
    :param env: AST Environment
    :return:    the result of the function's body execution
    """
    closure = ast[0]

    if len(ast[1:]) != len(closure.params):
        raise LispError('wrong number of arguments, expected %d got %d' % (len(closure.params), len(ast[1:])))

    args = dict()
    for idx, param in enumerate(ast[1:]):
        args[closure.params[idx]] = evaluate(param, env)

    call_env = closure.env.extend(args)
    return evaluate(closure.body, call_env)


def eval_math(ast, env):
    """
    Consume a list with a mathematical expression and return its evaluation.
    E.g.: ["+", 2, 10] ->
    :param ast: [math operator, exp1, exp2]
    :param env: AST Environment
    :return:    number
    """
    l_operand = evaluate(ast[1], env)
    r_operand = evaluate(ast[2], env)
    if type(l_operand) is str or type(r_operand) is str:
        raise LispError("One of the arguments is not a number: {} or {}".format(l_operand, r_operand))
    return eval(str(l_operand) + ast[0].replace("mod", "%") + str(r_operand))


def eval_cons(ast, env):
    """
    Consume a list with the first element == "cons" and produce a new list from
    the concatenation of the first parameter (atom) with the second (list or string).
    Eg.: ["cons", "ABC", [1, 2, 3]] -> ["ABC", 1, 2, 3]
    :param ast: ["cons", ABC, []]
    :param env: AST Environment
    :return:    list
    """
    item = evaluate(ast[1], env)
    container = evaluate(ast[2], env)

    if is_list(container):
        lst = list()
        lst.append(item)
        lst += container
        return lst

    if is_string(container):

        if is_string(item):
            return String(item.val + container.val)

        else:
            return String(str(item) + container.val)

    raise LispError("You can't use cons without a list or a string as a second argument: {}".format(ast))


def eval_empty(ast, env):
    """
    Consume a list or String and return true if it is empty.
    E.g.: ["empty", []] -> True
    :param ast: ["empty", []]
    :param env: AST Environment
    :return:    bool
    """
    lst = evaluate(ast[1], env)

    if is_list(lst) or is_string(lst):
        return True if len(lst) == 0 else False

    raise LispError('can\'t apply empty on something different than a list or a string')


def eval_head(ast, env):
    """
    Consume a list or String and return its first element.
    E.g.: ["head", [1, 2, 3]] -> 1
    :param ast: ["head", []]
    :param env: AST Environment
    :return:    first element of the list (atom or list)
    """
    lst = evaluate(ast[1], env)

    if not (is_list(lst) or is_string(lst)):
        raise LispError('can\'t apply head on something different than a list or a string')

    if len(lst) == 0:
        raise LispError('can\'t apply head on an empty list or string')

    else:
        return lst[0] if is_list(lst) else String(lst[0])


def eval_tail(ast, env):
    """
    Consume a list or String and return all of its elements minus the first one.
    E.g.: ["tail", [1, 2, 3]] -> [2, 3]
    :param ast: ["tail", []]
    :param env: AST Environment
    :return:    list
    """
    lst = evaluate(ast[1], env)

    if not (is_list(lst) or is_string(lst)):
        raise LispError('can\'t apply tail on something different than a list or a string')

    if len(lst) == 0:
        raise LispError('can\'t apply tail on an empty list or string')

    else:
        return lst[1:] if is_list(lst) else String(lst[1:])


def eval_quote(ast):
    """
    Consume a list with its first element equal to "quote" and return the second element (list)
    without being evaluated.
    ["quote", ["+", 1, 2]] -> ["+", 1, 2]
    :param ast: ["quote", []]
    :return:    the second element without being evaluated
    """
    return ast[1]


def eval_if(ast, env):
    """
    Consume a list with the first element equal to "if" and 3 additional elements (a condition,
    an expression for the true case and an expression for the false case), and return the result
    of the evaluation of one of the conditional expressions.
    E.g.: ["if", (">" 10 5), 10, 5] -> 10
    :param ast: ["if", expr condition, true expr, false expr]
    :param env: AST Environment
    :return:    the result of the evaluation of true expr or false expr
    """
    return evaluate(ast[2], env) if evaluate(ast[1], env) else evaluate(ast[3], env)


def eval_cond(ast, env):
    """
    Consume a list with the first element equal to "cond" and N number of tuples (list with
    two elements) and return the result of the execution of the condition that get evaluated
    as true.
    E.g.: ["cond", [ ["empty", [1, 2, 3]], [1, 2, 3] ] (Example with one condition)
    :param ast: ["cond", [ [], [] ], [ [], [] ], ..., [ [], [] ]]
    :param env: AST Environment
    :return:    the evaluation of the expression associated with a condition evaluated to true
    """
    predicates = list()
    expressions = list()

    conditions = ast[1]

    for cond_exp in conditions:

        if not is_list(cond_exp):
            raise LispError('Every condition must be a tuple (list) of a predicate and a expression.')

        predicates.append(cond_exp[0])
        expressions.append(cond_exp[1])

    for idx, p in enumerate(predicates):

        if evaluate(p, env):
            return evaluate(expressions[idx], env)

    return False
