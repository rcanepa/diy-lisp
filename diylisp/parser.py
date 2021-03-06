# -*- coding: utf-8 -*-

import re
from .ast import is_boolean, is_list
from .types import LispError, String

"""
This is the parser module, with the `parse` function which you'll implement as part 1 of
the workshop. Its job is to convert strings into data structures that the evaluator can 
understand. 
"""

debug = False


def parse(source):
    """Parse string representation of one *single* expression
    into the corresponding Abstract Syntax Tree."""

    global debug

    if source == '(cons "f" "oobar")':
        debug = True

    source = remove_comments(source).strip()

    if debug:
        print source

    tokens = token_converter(source)

    if debug:
        print tokens

    debug = False

    return tokens


def token_converter(token):
    """

    :param token: string token that needs to be converted
    :return: a list
    """

    global debug

    if token[0] == "'":
        lst = list(["quote"])
        lst.append(token_converter(token[1:]))
        return lst

    if token == "#f":
        return False

    if token == "#t":
        return True

    if token.isdigit():
        return int(token)

    if token[0] == "(":
        idx_matching_paren = find_matching_paren(token)

        if idx_matching_paren + 1 != len(token):
            raise LispError("Expected EOF: %s" % token)

        # Check if it is an empty list
        if idx_matching_paren == 1:
            return []

        else:

            tokens = split_exps(token[1:-1])

            lst = []
            for t in tokens:
                lst.append(token_converter(t))

            return lst

    if token[0] == "\"":

        if token[-1] != "\"":
            raise LispError("Unclosed string: {}".format(token))

        if re.search(r'([^\\]\")', token[1:-1]):
            raise LispError("Expected EOF (unescaped double quotes).")

        return String(token[1:-1])

    # The token doesn't need to be transformed
    return token

#
# Below are a few useful utility functions. These should come in handy when
# implementing `parse`. We don't want to spend the day implementing parenthesis
# counting, after all.
#


def remove_comments(source):
    """Remove from a string anything in between a ; and a linebreak"""
    return re.sub(r";.*\n", "\n", source)


def find_matching_paren(source, start=0):
    """Given a string and the index of an opening parenthesis, determines 
    the index of the matching closing paren."""

    assert source[start] == '('
    # print source
    pos = start
    open_brackets = 1
    double_quotes = 0

    while open_brackets > 0:
        pos += 1

        if len(source) == pos:
            raise LispError("Incomplete expression: %s" % source[start:])

        # Do not count parenthesis inside strings (surrounded by double quotes) and do not
        # count a escaped double quote.
        if source[pos] == "\"" and source[pos - 1] != "\\":
            double_quotes += 1

        if double_quotes % 2 == 0:

            if source[pos] == '(':
                open_brackets += 1

            if source[pos] == ')':
                open_brackets -= 1

    return pos


def split_exps(source):
    """Splits a source string into subexpressions 
    that can be parsed individually.

    Example: 

        > split_exps("foo bar (baz 123)")
        ["foo", "bar", "(baz 123)"]
    """

    rest = source.strip()

    exps = []
    while rest:
        exp, rest = first_expression(rest)
        exps.append(exp)

    return exps


def first_expression(source):
    """Split string into (exp, rest) where exp is the 
    first expression in the string and rest is the 
    rest of the string after this expression."""
    
    source = source.strip()

    if source[0] == "'":
        exp, rest = first_expression(source[1:])
        return source[0] + exp, rest

    elif source[0] == "(":
        last = find_matching_paren(source)
        return source[:last + 1], source[last + 1:]

    elif source[0] == "\"":
        double_quotes_end = find_closing_double_quotes(source)
        atom = source[:double_quotes_end]
        return atom, source[double_quotes_end:]

    else:
        match = re.match(r"^[^\s)(']+", source)
        end = match.end()
        atom = source[:end]
        return atom, source[end:]


def find_closing_double_quotes(source):
    """
    Consume a string that start with an " and return the position of the
    next " escaping " \" ".

    Regular expression: "([^"\\]|\\.)*"
                        Two quotes surrounding zero or more of any character that's not a quote or a backslash
                        or a backslash followed by any character.

    :param source:  string
    :return:        integer
    """
    assert source[0] == "\""

    match = re.match(r'"([^"\\]|\\.)*"', source)

    if match is None:
        raise LispError("Incomplete expression, you must finish the string with a double quote: {}".format(source))

    return match.end()


#
# The functions below, `parse_multiple` and `unparse` are implemented in order for
# the REPL to work. Don't worry about them when implementing the language.
#


def parse_multiple(source):
    """Creates a list of ASTs from program source constituting multiple expressions.

    Example:

        >>> parse_multiple("(foo bar) (baz 1 2 3)")
        [['foo', 'bar'], ['baz', 1, 2, 3]]

    """

    source = remove_comments(source)
    return [parse(exp) for exp in split_exps(source)]


def unparse(ast):
    """Turns an AST back into lisp program source"""

    if is_boolean(ast):
        return "#t" if ast else "#f"

    elif is_list(ast):

        if len(ast) > 0 and ast[0] == "quote":
            return "'%s" % unparse(ast[1])

        else:
            return "(%s)" % " ".join([unparse(x) for x in ast])

    else:
        # integers or symbols (or lambdas)
        return str(ast)
