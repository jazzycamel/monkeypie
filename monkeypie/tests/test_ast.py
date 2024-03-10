import unittest

from monkeypie.ast import ProgramNode, LetStatement, IdentifierExpression
from monkeypie.token import Token, TokenType


class TestStrings(unittest.TestCase):
    def test_string(self):
        program = ProgramNode()
        program.statements = [
            LetStatement(
                Token(TokenType.LET, "let"),
                IdentifierExpression(Token(TokenType.IDENT, "myVar"), "myVar"),
                IdentifierExpression(
                    Token(TokenType.IDENT, "anotherVar"), "anotherVar"
                ),
            )
        ]
        self.assertEqual("let myVar = anotherVar;", str(program))
