from monkeypie.ast import (
    ProgramNode,
    StatementNode,
    LetStatement,
    IdentifierExpression,
    ReturnStatement,
)
from monkeypie.lexer import Lexer
from monkeypie.token import Token, TokenType


class Parser:
    current_token: Token = Token(TokenType.ILLEGAL, "")
    peek_token: Token = Token(TokenType.ILLEGAL, "")

    def __init__(self, lexer: Lexer):
        self._lexer = lexer
        self._errors: list[str] = []

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
        return None

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
