from enum import Enum
from typing import Final


class TokenType(Enum):
    ILLEGAL = "ILLEGAL"
    EOF = "EOF"

    # Identifiers
    IDENT = "IDENT"
    INT = "INT"

    # Operators
    ASSIGN = "="
    PLUS = "+"
    MINUS = "-"
    BANG = "!"
    ASTERISK = "*"
    SLASH = "/"
    LT = "<"
    GT = ">"
    EQ = "=="
    NOT_EQ = "!="

    # Delimiters
    COMMA = ","
    SEMICOLON = ";"
    LPAREN = "("
    RPAREN = ")"
    LBRACE = "{"
    RBRACE = "}"

    # Keywords
    FUNCTION = "FUNCTION"
    LET = "LET"
    TRUE = "TRUE"
    FALSE = "FALSE"
    IF = "IF"
    ELSE = "ELSE"
    RETURN = "RETURN"


KEYWORDS: Final[dict[str, TokenType]] = {
    "fn": TokenType.FUNCTION,
    "let": TokenType.LET,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "return": TokenType.RETURN,
}


class Token:
    def __init__(self, token_type: TokenType, literal: str):
        self.type = token_type
        self.literal = literal

    def __str__(self):
        return f"Token {{ Type:{self.type}, Literal:{self.literal} }}"
