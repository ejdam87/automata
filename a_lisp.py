# Write a simple LISP (expression) parser, following this EBNF grammar:
#
#     expression  = atom | compound ;
#     compound    = '(', expression, { whitespace, expression }, ')' |
#                   '[', expression, { whitespace, expression }, ']' ;
#     whitespace  = ( ' ' | ? newline ? ), { ' ' | ? newline ? } ;
#     atom        = literal | identifier ;
#     literal     = number | string | bool ;
#
#     nonzero    = '1' | '2' | '3' | '4' |
#                  '5' | '6' | '7' | '8' | '9' ;
#     digit      = '0' | nonzero ;
#     sign       = '+' | '-' ;
#     digits     = '0' | ( nonzero, { digit } ) ;
#     number     = [ sign ], digits, [ '.', { digit } ] ;
#
#     bool       = '#f' | '#t' ;
#
#     string     = '"', { str_char }, '"' ;
#     str_lit    = ? any character except '"' and '\' ? ;
#     str_esc    = '\"' | '\\' ;
#     str_char   = str_lit | str_esc ;
#
#     identifier = id_init, { id_subseq } | sign ;
#     id_init    = id_alpha | id_symbol ;
#     id_symbol  = '!' | '$' | '%' | '&' | '*' | '/' | ':' | '<' |
#                  '=' | '>' | '?' | '_' | '~' ;
#     id_alpha   = ? alphabetic character ?
#     id_subseq  = id_init | digit | id_special ;
#     id_special = '+' | '-' | '.' | '@' | '#' ;
#
# Alphabetic characters are those for which ‹isalpha()› returns
# ‹True›. It is okay to accept additional whitespace where it makes
# sense. For the semantics of (ISO) EBNF, see e.g. wikipedia.
#
# The parser should be implemented as a toplevel function called
# ‹parse› that takes a single ‹str› argument. If the string does not
# conform to the above grammar, return ‹None›. Assuming ‹expr› is a
# string with a valid expression, the following should hold about
# ‹x = parse(expr)›:
#
#  • an ‹x.is_foo()› method is provided for each of the major
#    non-terminals: ‹compound›, ‹atom›, ‹literal›, ‹bool›, ‹number›,
#    ‹string› and ‹identifier› (e.g. there should be an ‹is_atom()›
#    method), returning a boolean,
#  • if ‹x.is_compound()› is true, ‹len(x)› should be a valid
#    expression and ‹x› should be iterable, yielding sub-expressions
#    as objects which also implement this same interface,
#  • if ‹x.is_bool()› is true, ‹bool(x)› should work,
#  • if ‹x.is_number()› is true, basic arithmetic (‹+›, ‹-›, ‹*›,
#    ‹/›) and relational (‹<›, ‹>›, ‹==›, ‹!=›) operators should
#    work (e.g.  ‹x < 7›, or ‹x * x›) as well as ‹int(x)› and
#    ‹float(x)›,
#  • ‹x == parse(expr)› should be true (i.e. equality should be
#    extensional),
#  • ‹x == parse(str(x))› should also hold.
#
# If a numeric literal ‹x› with a decimal dot is directly converted to
# an ‹int›, this should behave the same as ‹int( float( x ) )›. A few
# examples of valid inputs (one per line):
#
#     (+ 1 2 3)
#     (eq? [quote a b c] (quote a c b))
#     12.7
#     (concat "abc" "efg" "ugly \"string\"")
#     (set! var ((stuff) #t #f))
#     (< #t #t)
#
# Note that ‹str(parse(expr)) == expr› does «not» need to hold.
# Instead, ‹str› should always give a canonical representation,
# e.g. this must hold:
#
#     str( parse( '+7' ) ) == str( parse( '7' ) )

from typing import List, Union, Iterator, Dict, Callable, Optional
from operator import add, sub, truediv, mul

ID_SYMBOLS = {'!', '$', '%', '&', '*', '/',
           ':','<', '=', '>', '?', '_', '~'}

ID_SPEACIAL = {'+', '-', '.', '@', '#'}

Literal = Union["Boolean", "Number", "String"]
Atom = Union["Literal", "Identifier"]

class Expression:

    def __init__(self, val: Union[str, bool, int, float]) -> None:
        self.val = val

    def is_atom(self) -> bool:
        return self.is_literal() or self.is_identifier()

    def is_compound(self) -> bool:
        return isinstance(self, Compound)

    def is_bool(self) -> bool:
        return isinstance(self, Boolean)

    def is_string(self) -> bool:
        return isinstance(self, String)

    def is_number(self) -> bool:
        return isinstance(self, Number)

    def is_identifier(self) -> bool:
        return isinstance(self, Identifier)
    
    def is_literal(self) -> bool:
        return self.is_bool() or self.is_string() or self.is_number()

class Boolean( Expression ):
    def __init__(self, val: bool) -> None:
        self.val: bool = val

    def __repr__(self) -> str:
        return "#t" if self.val else "#f"

    def __bool__(self) -> bool:
        return self.val

    def __eq__(self, other: object) -> bool:

        if isinstance(other, bool):
            return self.val == other

        if isinstance(other, Boolean):
            return self.val == other.val

        return False

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)


Ops_type = Dict[str, Callable[[float, float], float]]
Numeric_type = Union["Number", int, float]
class Number( Expression ):

    OPS: Ops_type = {"+": add,
                     "-": sub,
                     "*": mul,
                     "/": truediv}

    def __init__(self, val: float) -> None:
        self.val: float = val

    def __int__(self) -> int:
        return int(self.val)

    def __float__(self) -> float:
        return float(self.val)

    def __repr__(self) -> str:
        return str(self.val)

    def __add__(self, other: Numeric_type) -> "Number":
        if isinstance(other, Number):
            return Number(Number.OPS["+"](self.val, other.val))

        return Number(Number.OPS["+"](self.val, other))

    def __mul__(self, other: Numeric_type) -> "Number":
        if isinstance(other, Number):
            return Number(Number.OPS["*"](self.val, other.val))

        return Number(Number.OPS["*"](self.val, other))

    def __sub__(self, other: Numeric_type) -> "Number":
        if isinstance(other, Number):
            return Number(Number.OPS["-"](self.val, other.val))

        return Number(Number.OPS["-"](self.val, other))

    def __rsub__(self, other: Numeric_type) -> "Number":
        if isinstance(other, Number):
            return Number(Number.OPS["-"](other.val, self.val))

        return Number(Number.OPS["-"](other, self.val))

    def __floordiv__(self, other: Numeric_type) -> "Number":
        return self.__div__(other)

    def __div__(self, other: Numeric_type) -> "Number":
        if isinstance(other, Number):
            return Number(Number.OPS["/"](self.val, other.val))

        return Number(Number.OPS["/"](self.val, other))

    def __rdiv__(self, other: Numeric_type) -> "Number":
        if isinstance(other, Number):
            return Number(Number.OPS["/"](other.val, self.val))

        return Number(Number.OPS["/"](other, self.val))
    
    def __rfloordiv__(self, other: Numeric_type) -> "Number":
        return self.__rdiv__(other)

    def __eq__(self, other: object) -> bool:
        
        if isinstance(other, Number):
            return self.val == other.val

        if isinstance(other, int):
            return self.val == other

        if isinstance(other, float):
            return self.val == other

        return False

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __lt__(self, other: Numeric_type) -> bool:
        
        if isinstance(other, Number):
            return self.val < other.val

        return self.val < other

    def __gt__(self, other: Numeric_type) -> bool:
        if isinstance(other, Number):
            return self.val > other.val

        return self.val > other

    __radd__ = __add__
    __rmul__ = __mul__


class Identifier( Expression ):
    def __init__(self, val: str) -> None:
        self.val: str = val

    def __repr__(self) -> str:
        return str(self.val)

    def __eq__(self, other: object) -> bool:

        if isinstance(other, Identifier):
            return self.val == other.val

        return False

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

class String( Expression ):
    def __init__(self, val: str) -> None:
        self.val: str = val

    def __repr__(self) -> str:

        to_print = self.val.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{to_print}"'

    def __eq__(self, other: object) -> bool:

        if isinstance(other, str):
            return self.val == other

        if isinstance(other, String):
            return self.val == other.val

        return False

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)


class Compound( Expression ):
    def __init__(self, vals: List[ Expression ]) -> None:
        self.vals = vals

    def __repr__(self) -> str:
        text = [str(val) for val in self.vals]
        return f'({" ".join(text)})'

    def __iter__(self) -> Iterator[Expression]:
        for val in self.vals:
            yield val

    def __len__(self) -> int:
        return len(self.vals)

    def __eq__(self, other: object) -> bool:

        if not isinstance(other, Compound):
            return False

        if len(self) != len(other):
            return False

        for v1, v2 in zip(self.vals, other.vals):
            if v1 != v2:
                return False

        return True

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)


class Parser:
    def __init__(self, text: str) -> None:
        self.error = False
        self.text = text
        self.pos = 0

    def nxt(self) -> str:
        curr = self.peek()
        self.pos += 1
        return curr

    def end(self) -> bool:
        return self.error == True or self.pos >= len(self.text)

    def peek(self) -> str:
        return self.text[self.pos] if not self.end() else ""

    def peek_next(self, offset: int) -> str:
        return self.text[self.pos + offset] if self.pos + offset < len(self.text) else ""

    def require_group(self, cs: List[str]) -> None:
        if self.nxt() not in cs:
            self.error = True

    def require(self, c: str) -> None:
        if self.nxt() != c:
            self.error = True

    def after_atom(self) -> None:

        if self.end():
            return

        if self.peek() not in ["\n", " ", ")", "]"]:
            self.error = True

    def parse(self) -> Expression:
        res = self.expression()
        if self.pos <= len(self.text) - 1:
            self.error = True

        return res

    def expression(self) -> Expression:
        
        if self.is_opening_bracket():
            return self.compound()
        else:
            return self.atom()

    def number(self) -> Number:

        val = ""
        sign = 1
        if self.peek() == "-":
            sign = -1

        if self.is_sign():
            self.nxt()

        has_dot = False
    
        while self.is_digit() or self.peek() == ".":

            if self.peek() == ".":
                if has_dot:
                    self.eror = True
                    break

                has_dot = True

            val += self.nxt()

        res_val = float(val) if self.is_float(val) else int(val)

        if val[0] == "0" and len(val) != 1:
            if val[1] != ".":
                self.error = True

        return Number( sign * res_val )

    def _bool(self) -> Boolean:
        self.require("#")
        symbol = self.nxt()
        if symbol == "t":
            res = True
        elif symbol == "f":
            res = False
        else:
            self.error = True

        return Boolean( res )

    def string(self) -> String:
        
        res = ""
        self.require('"')

        while self.peek() != '"':
            if self.end():
                self.error = True
                break

            if self.peek() == "\\":
                if self.peek_next(1) == '"':
                    self.nxt()
                elif self.peek_next(1) == "\\":
                    self.nxt()
                else:
                    self.error = True
                    break

            res += self.nxt()

        self.require('"')

        return String( res )

    def identifier(self) -> Identifier:

        if self.is_sign():
            val = self.nxt()
            return Identifier( val )

        val = ""
        while (not self.end()) and self.is_id_sub():
            val += self.nxt()

        return Identifier( val )

    def atom(self) -> Atom:

        val: Union[Literal, Identifier] = Boolean(True)   # Just default value

        self.skip_spaces()
        if self.is_number():
            val = self.number()
        elif self.is_bool():
            val = self._bool()
        elif self.is_string():
            val = self.string()
        elif self.is_identifier():
            val = self.identifier()
        else:
            self.error = True

        self.after_atom()
        return val

    def compound(self) -> Compound:

        vals = []

        if self.peek() == "(":
            bracket = "("
        else:
            bracket = "["

        self.require(bracket)

        while not self.end():
            val = self.expression()
            vals.append(val)
            self.skip_spaces()
            if self.is_closing_bracket():
                break

        self.require(")" if bracket == "(" else "]")
        return Compound(vals)

    def skip_spaces(self) -> None:
        while self.is_whitespace():
            self.nxt()

    def is_sign(self) -> bool:
        return self.peek() in ["+", "-"]

    def is_nonzero(self) -> bool:
        return self.peek() in [str(i) for i in range(1, 10)]

    def is_digit(self) -> bool:
        return self.peek() == "0" or self.is_nonzero()

    def is_bracket(self) -> bool:
        return self.is_opening_bracket() or self.is_closing_bracket()

    def is_opening_bracket(self) -> bool:
        return self.peek() == "(" or self.peek() == "["

    def is_closing_bracket(self) -> bool:
        return self.peek() == ")" or self.peek() == "]"

    def is_whitespace(self) -> bool:
        return self.peek() == " " or self.peek() == "\n"

    def is_float(self, num: str) -> bool:
        return "." in num

    def is_alpha(self) -> bool:
        return self.peek().isalpha()

    def is_id_symbol(self) -> bool:
        return self.peek() in ID_SYMBOLS

    def is_id_init(self) -> bool:
        return self.is_alpha() or self.is_id_symbol()

    def is_id_sub(self) -> bool:
        return self.is_id_init() or self.is_digit() or self.peek() in ID_SPEACIAL

#     identifier = id_init, { id_subseq } | sign ;
#     id_init    = id_alpha | id_symbol ;
#     id_symbol  = '!' | '$' | '%' | '&' | '*' | '/' | ':' | '<' |
#                  '=' | '>' | '?' | '_' | '~' ;
#     id_alpha   = ? alphabetic character ?
#     id_subseq  = id_init | digit | id_special ;
#     id_special = '+' | '-' | '.' | '@' | '#' ;

    def is_identifier(self) -> bool:
        nxt = self.peek_next(1)
        sign_ident = self.is_sign() and nxt in ["", " ", "\n", ")", "]"]
        return sign_ident or self.is_id_init()

    def is_string(self) -> bool:
        return self.peek() == '"'

    def is_number(self) -> bool:
        nxt = self.peek_next(1)
        signed = self.is_sign() and nxt.isdigit()
        return self.is_digit() or signed

    def is_bool(self) -> bool:
        return self.peek() == "#" and self.peek_next(1) in ["t", "f"]

def parse(text: str) -> Optional[Expression]:
    p = Parser(text)
    res = p.parse()
    return res if not p.error else None
