from enum import auto, IntEnum
from typing import Callable

from monkeypie.ast import (
    ProgramNode,
    StatementNode,
    LetStatement,
    IdentifierExpression,
    ReturnStatement,
    ExpressionNode,
    ExpressionStatement,
    IntegerLiteralExpression,
    PrefixExpression,
)
from monkeypie.lexer import Lexer
from monkeypie.token import Token, TokenType

PrefixParseFn = Callable[[], ExpressionNode | None]
InfixParseFn = Callable[[ExpressionNode], ExpressionNode]


class Precedence(IntEnum):
    LOWEST = auto()
    EQUALS = auto()
    LESS_GREATER = auto()
    SUM = auto()
    PRODUCT = auto()
    PREFIX = auto()
    CALL = auto()


class Parser:
    current_token: Token = Token(TokenType.ILLEGAL, "")
    peek_token: Token = Token(TokenType.ILLEGAL, "")

    def __init__(self, lexer: Lexer):
        self._lexer = lexer
        self._errors: list[str] = []

        self._prefix_parse_functions: dict[TokenType, PrefixParseFn] = {}
        self._infix_parse_functions: dict[TokenType, InfixParseFn] = {}

        self.register_prefix_parse_function(TokenType.IDENT, self.parse_identifier)
        self.register_prefix_parse_function(
            TokenType.INT, self.parse_integer_literal_expression
        )
        self.register_prefix_parse_function(
            TokenType.BANG, self.parse_prefix_expression
        )
        self.register_prefix_parse_function(
            TokenType.MINUS, self.parse_prefix_expression
        )

        self.next_token()
        self.next_token()

    def errors(self):
        return self._errors

    def next_token(self):
        self.current_token = self.peek_token
        self.peek_token = self._lexer.next_token()

    def current_token_is(self, type: TokenType) -> bool:
        return self.current_token.type == type

    def peek_token_is(self, type: TokenType) -> bool:
        return self.peek_token.type == type

    def peek_error(self, type: TokenType):
        self._errors.append(
            f"expected next token to be {type}, got {self.peek_token.type} instead"
        )

    def expect_peek(self, type: TokenType) -> bool:
        if self.peek_token_is(type):
            self.next_token()
            return True
        self.peek_error(type)
        return False

    def register_prefix_parse_function(
        self, token_type: TokenType, prefix_parse_function: PrefixParseFn
    ) -> None:
        self._prefix_parse_functions[token_type] = prefix_parse_function

    def register_infix_parse_function(
        self, token_type: TokenType, infix_parse_function: InfixParseFn
    ) -> None:
        self._infix_parse_functions[token_type] = infix_parse_function

    def parse_program(self) -> ProgramNode | None:
        program = ProgramNode()
        while self.current_token.type != TokenType.EOF:
            statement = self.parse_statement()
            if statement:
                program.statements.append(statement)
            self.next_token()

        return program

    def parse_statement(self) -> StatementNode | None:
        match self.current_token.type:
            case TokenType.LET:
                return self.parse_let_statement()
            case TokenType.RETURN:
                return self.parse_return_statement()
            case _:
                return self.parse_expression_statement()

    def parse_let_statement(self) -> LetStatement | None:
        statement = LetStatement(self.current_token)
        if not self.expect_peek(TokenType.IDENT):
            return None

        statement.name = IdentifierExpression(
            self.current_token, self.current_token.literal
        )
        if not self.expect_peek(TokenType.ASSIGN):
            return None

        # TODO: skip expressions until semicolon
        while not self.current_token_is(TokenType.SEMICOLON):
            self.next_token()

        return statement

    def parse_return_statement(self) -> ReturnStatement:
        statement = ReturnStatement(self.current_token)

        self.next_token()

        # TODO: skip expressions until semicolon
        while not self.current_token_is(TokenType.SEMICOLON):
            self.next_token()

        return statement

    def parse_expression_statement(self) -> ExpressionStatement:
        statement = ExpressionStatement(self.current_token)
        statement.expression = self.parse_expression(Precedence.LOWEST)

        if self.peek_token_is(TokenType.SEMICOLON):
            self.next_token()
        return statement

    def parse_expression(self, precedence: Precedence) -> ExpressionNode | None:
        try:
            prefix = self._prefix_parse_functions[self.current_token.type]
        except KeyError:
            self._errors.append(
                f"no prefix parse function found for {self.current_token.type.value} found"
            )
            return None
        return prefix()

    def parse_identifier(self) -> ExpressionNode:
        return IdentifierExpression(self.current_token, self.current_token.literal)

    def parse_integer_literal_expression(self) -> ExpressionNode | None:
        literal = IntegerLiteralExpression(self.current_token)

        try:
            literal.value = int(self.current_token.literal)
            return literal
        except ValueError:
            self._errors.append(
                f"could not parse {self.current_token.literal} as integer"
            )
            return None

    def parse_prefix_expression(self) -> ExpressionNode:
        expression = PrefixExpression(self.current_token, self.current_token.literal)
        self.next_token()
        expression.right = self.parse_expression(Precedence.PREFIX)
        return expression
