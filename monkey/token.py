# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/


from dataclasses import dataclass
from enum import Enum, auto
from logging.config import IDENTIFIER


class TokenType(Enum):
    ILLEGAL = "ILLEGAL"
    EOF = "EOF"

    IDENT = "IDENT"
    INT = "INT"
    STRING = "STRING"
    
    COMMA = ","
    SEMICOLON = ";"
    LPAREN = "("
    RPAREN = ")"
    LBRACE = "{"
    RBRACE = "}"
    LBRACKET = "["
    RBRACKET = "]"

    FUNCTION = "FUNCTION"
    LET      = "LET"
    TRUE     = "TRUE"
    FALSE    = "FALSE"
    IF       = "IF"
    ELSE     = "ELSE"
    RETURN   = "RETURN"

    ASSIGN   = "="
    PLUS     = "+"
    MINUS    = "-"
    BANG     = "!"
    ASTERISK = "*"
    SLASH    = "/"

    LT = "<"
    GT = ">"

    EQ = "=="
    NOT_EQ = "!="



@dataclass
class Token:
    type: TokenType
    literal: str


KEYWORDS = {
    "fn": TokenType.FUNCTION,
    "let": TokenType.LET,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "return": TokenType.RETURN,
}


def lookup_ident(ident) -> TokenType:
    return KEYWORDS.get(ident, TokenType.IDENT)
