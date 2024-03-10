import unittest
from typing import cast

from monkeypie.ast import (
    LetStatement,
    StatementNode,
    ReturnStatement,
    ExpressionStatement,
    IdentifierExpression,
)
from monkeypie.lexer import Lexer
from monkeypie.parser import Parser


def check_parser_errors(test_case: unittest.TestCase, parser: Parser) -> None:
    errors = parser.errors()
    if len(errors) == 0:
        return
    test_case.assertEqual(
        0, len(errors), "\n".join([f"parser error: {e}" for e in errors])
    )


class TestLetStatements(unittest.TestCase):
    def _test_let_statement(self, statement: StatementNode, name: str) -> bool:
        self.assertEqual("let", statement.token_literal())
        self.assertIsInstance(statement, LetStatement)
        statement = cast(LetStatement, statement)
        self.assertEqual(statement.name.value, name)
        self.assertTrue(statement.name.token_literal(), name)
        return True

    def test_let_statements(self):
        input = r"""
let x = 5;
let y = 10;
let foobar = 838383;
"""
        lexer = Lexer(input)
        parser = Parser(lexer)
        program = parser.parse_program()
        check_parser_errors(self, parser)
        self.assertIsNotNone(program)
        self.assertEqual(3, len(program.statements))

        for i, expected in enumerate(["x", "y", "foobar"]):
            statement = program.statements[i]
            self.assertTrue(self._test_let_statement(statement, expected))


class TestReturnStatements(unittest.TestCase):
    def test_return_statements(self):
        input = r"""
return 5;
return 10;
return 993322;
"""
        lexer = Lexer(input)
        parser = Parser(lexer)
        program = parser.parse_program()
        check_parser_errors(self, parser)
        self.assertIsNotNone(program)
        self.assertEqual(3, len(program.statements))

        for statement in program.statements:
            self.assertIsInstance(statement, ReturnStatement)
            self.assertEqual(statement.token_literal(), "return")


class TestIdentifierExpressions(unittest.TestCase):
    def test_identifier_expressions(self):
        input = "foobar;"
        lexer = Lexer(input)
        parser = Parser(lexer)
        program = parser.parse_program()
        check_parser_errors(self, parser)
        self.assertIsNotNone(program)
        self.assertEqual(1, len(program.statements))

        statement = program.statements[0]
        self.assertIsInstance(statement, ExpressionStatement)
        statement = cast(ExpressionStatement, statement)
        identifier = statement.expression
        self.assertIsInstance(identifier, IdentifierExpression)
        identifier = cast(IdentifierExpression, identifier)
        self.assertEqual("foobar", identifier.value)
        self.assertEqual("foobar", identifier.token_literal())
