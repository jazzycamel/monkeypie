import os
from enum import auto, IntEnum
from functools import partial
from typing import Callable, Final

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
    InfixExpression,
    BooleanLiteralExpression,
    IfExpression,
    BlockStatement,
    FunctionLiteralExpression,
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


PRECEDENCES: Final[dict[TokenType, Precedence]] = {
    TokenType.EQ: Precedence.EQUALS,
    TokenType.NOT_EQ: Precedence.EQUALS,
    TokenType.LT: Precedence.LESS_GREATER,
    TokenType.GT: Precedence.LESS_GREATER,
    TokenType.PLUS: Precedence.SUM,
    TokenType.MINUS: Precedence.SUM,
    TokenType.SLASH: Precedence.PRODUCT,
    TokenType.ASTERISK: Precedence.PRODUCT,
}


class Trace:
    level: int = 0

    def __init__(self, wrapped: Callable):
        self._wrapped = wrapped
        if os.environ.get("MONKEYPIE_PARSE_TRACE_ENABLED", None):
            self._action = self._trace_action
        else:
            self._action = self._wrapped

    def __get__(self, instance, owner):
        return partial(self.__call__, instance)

    def __call__(self, *args, **kwargs):
        return self._action(*args, **kwargs)

    def _trace_action(self, *args, **kwargs):
        Trace.level += 1
        indent = "\t" * (Trace.level - 1)
        print(f"{indent}BEGIN:", self._wrapped.__name__, args[1:], kwargs)
        result = self._wrapped(*args, **kwargs)
        print(f"{indent}END:", self._wrapped.__name__)
        Trace.level -= 1
        return result


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
        self.register_prefix_parse_function(
            TokenType.TRUE, self.parse_boolean_literal_expression
        )
        self.register_prefix_parse_function(
            TokenType.FALSE, self.parse_boolean_literal_expression
        )
        self.register_prefix_parse_function(
            TokenType.LPAREN, self.parse_grouped_expression
        )
        self.register_prefix_parse_function(TokenType.IF, self.parse_if_expression)
        self.register_prefix_parse_function(
            TokenType.FUNCTION, self.parse_function_literal
        )

        self.register_infix_parse_function(TokenType.PLUS, self.parse_infix_expression)
        self.register_infix_parse_function(TokenType.MINUS, self.parse_infix_expression)
        self.register_infix_parse_function(TokenType.SLASH, self.parse_infix_expression)
        self.register_infix_parse_function(
            TokenType.ASTERISK, self.parse_infix_expression
        )
        self.register_infix_parse_function(TokenType.EQ, self.parse_infix_expression)
        self.register_infix_parse_function(
            TokenType.NOT_EQ, self.parse_infix_expression
        )
        self.register_infix_parse_function(TokenType.LT, self.parse_infix_expression)
        self.register_infix_parse_function(TokenType.GT, self.parse_infix_expression)

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

    def peek_precedence(self) -> Precedence:
        try:
            return PRECEDENCES[self.peek_token.type]
        except KeyError:
            return Precedence.LOWEST

    def current_precedence(self) -> Precedence:
        try:
            return PRECEDENCES[self.current_token.type]
        except KeyError:
            return Precedence.LOWEST

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

    @Trace
    def parse_expression_statement(self) -> ExpressionStatement:
        statement = ExpressionStatement(self.current_token)
        statement.expression = self.parse_expression(Precedence.LOWEST)
        if self.peek_token_is(TokenType.SEMICOLON):
            self.next_token()
        return statement

    @Trace
    def parse_expression(self, precedence: Precedence) -> ExpressionNode | None:
        try:
            prefix = self._prefix_parse_functions[self.current_token.type]
        except KeyError:
            self._errors.append(
                f"no prefix parse function found for {self.current_token.type.value} found"
            )
            return None

        left = prefix()
        if not left:
            return None
        while (
            not self.peek_token_is(TokenType.SEMICOLON)
            and precedence < self.peek_precedence()
        ):
            try:
                infix = self._infix_parse_functions[self.peek_token.type]
            except KeyError:
                return left
            self.next_token()
            left = infix(left)

        return left

    def parse_identifier(self) -> ExpressionNode:
        return IdentifierExpression(self.current_token, self.current_token.literal)

    @Trace
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

    @Trace
    def parse_prefix_expression(self) -> ExpressionNode:
        expression = PrefixExpression(self.current_token, self.current_token.literal)
        self.next_token()
        expression.right = self.parse_expression(Precedence.PREFIX)
        return expression

    @Trace
    def parse_infix_expression(self, left: ExpressionNode) -> ExpressionNode:
        expression = InfixExpression(
            self.current_token, left, self.current_token.literal
        )
        precedence = self.current_precedence()
        self.next_token()
        expression.right = self.parse_expression(precedence)
        return expression

    @Trace
    def parse_boolean_literal_expression(self) -> ExpressionNode:
        return BooleanLiteralExpression(
            self.current_token, self.current_token_is(TokenType.TRUE)
        )

    @Trace
    def parse_grouped_expression(self) -> ExpressionNode | None:
        self.next_token()
        expression = self.parse_expression(Precedence.LOWEST)
        if not self.expect_peek(TokenType.RPAREN):
            return None
        return expression

    @Trace
    def parse_if_expression(self) -> ExpressionNode | None:
        expression = IfExpression(self.current_token)
        if not self.expect_peek(TokenType.LPAREN):
            return None
        self.next_token()
        expression.condition = self.parse_expression(Precedence.LOWEST)
        if not self.expect_peek(TokenType.RPAREN):
            return None
        if not self.expect_peek(TokenType.LBRACE):
            return None
        expression.consequence = self.parse_block_statement()

        if self.peek_token_is(TokenType.ELSE):
            self.next_token()
            if not self.expect_peek(TokenType.LBRACE):
                return None
            expression.alternative = self.parse_block_statement()
        return expression

    @Trace
    def parse_block_statement(self) -> StatementNode | None:
        block = BlockStatement(self.current_token)
        self.next_token()
        while not self.current_token_is(TokenType.RBRACE) and not self.current_token_is(
            TokenType.EOF
        ):
            statement = self.parse_statement()
            if statement:
                block.statements.append(statement)
            self.next_token()
        return block

    @Trace
    def parse_function_literal(self) -> ExpressionNode | None:
        literal = FunctionLiteralExpression(self.current_token)
        if not self.expect_peek(TokenType.LPAREN):
            return None
        literal.parameters = self.parse_function_parameters()
        if not self.expect_peek(TokenType.LBRACE):
            return None
        literal.body = self.parse_block_statement()
        return literal

    def parse_function_parameters(self) -> list[IdentifierExpression]:
        identifiers: list[IdentifierExpression] = []
        if self.peek_token_is(TokenType.RPAREN):
            self.next_token()
            return identifiers
        self.next_token()
        identifier = IdentifierExpression(
            self.current_token, self.current_token.literal
        )
        identifiers.append(identifier)
        while self.peek_token_is(TokenType.COMMA):
            self.next_token()
            self.next_token()
            identifier = IdentifierExpression(
                self.current_token, self.current_token.literal
            )
            identifiers.append(identifier)
        if not self.expect_peek(TokenType.RPAREN):
            return []
        return identifiers
