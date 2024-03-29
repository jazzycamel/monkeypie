import unittest
from typing import cast

from parameterized import parameterized

from monkeypie.ast import (
    LetStatement,
    StatementNode,
    ReturnStatement,
    ExpressionStatement,
    IdentifierExpression,
    IntegerLiteralExpression,
    PrefixExpression,
    ExpressionNode,
    InfixExpression,
    ProgramNode,
    BooleanLiteralExpression,
    IfExpression,
    FunctionLiteralExpression,
    CallExpression,
)
from monkeypie.lexer import Lexer
from monkeypie.parser import Parser


class ParserTestCase(unittest.TestCase):
    def check_parser_errors(self, parser: Parser) -> None:
        errors = parser.errors()
        if len(errors) == 0:
            return
        self.assertEqual(
            0, len(errors), "\n".join([f"parser error: {e}" for e in errors])
        )

    def _test_execution(
        self,
        input: str,
        expected_statement_count: int | None = None,
    ) -> ProgramNode:
        lexer = Lexer(input)
        parser = Parser(lexer)
        program = parser.parse_program()
        self.check_parser_errors(parser)
        self.assertIsNotNone(program)
        assert program is not None
        if expected_statement_count is not None:
            self.assertEqual(expected_statement_count, len(program.statements))
        return program

    def _test_integer_literal(
        self, expression: ExpressionNode | None, value: int
    ) -> bool:
        self.assertIsInstance(expression, IntegerLiteralExpression)
        integer = cast(IntegerLiteralExpression, expression)
        self.assertEqual(value, integer.value)
        self.assertEqual(f"{integer.value}", integer.token_literal())
        return True

    def _test_identifier_literal(self, expression: ExpressionNode, value: str) -> bool:
        self.assertIsInstance(expression, IdentifierExpression)
        identifier = cast(IdentifierExpression, expression)
        self.assertEqual(value, identifier.value)
        self.assertEqual(value, identifier.token_literal())
        return True

    def _test_boolean_literal(self, expression: ExpressionNode, value: bool) -> bool:
        self.assertIsInstance(expression, BooleanLiteralExpression)
        boolean = cast(BooleanLiteralExpression, expression)
        self.assertEqual(value, boolean.value)
        self.assertEqual(str(boolean.value).lower(), boolean.token_literal())
        return True

    def _test_infix_expression(
        self,
        expression: ExpressionNode,
        left: int | str,
        operator: str,
        right: int | str,
    ) -> bool:
        self.assertIsInstance(expression, InfixExpression)
        infix = cast(InfixExpression, expression)
        if not (infix.left and infix.right):
            return False
        self.assertTrue(self._test_literal_expression(infix.left, left))
        self.assertEqual(operator, infix.operator)
        self.assertTrue(self._test_literal_expression(infix.right, right))
        return True

    def _test_literal_expression(
        self, expression: ExpressionNode, expected: int | str | bool
    ) -> bool:
        match type(expected).__name__:
            case "int":
                return self._test_integer_literal(expression, cast(int, expected))
            case "str":
                return self._test_identifier_literal(expression, cast(str, expected))
            case "bool":
                return self._test_boolean_literal(expression, cast(bool, expected))
        return False


class TestLetStatements(ParserTestCase):
    def _test_let_statement(self, statement: StatementNode, name: str) -> bool:
        self.assertEqual("let", statement.token_literal())
        self.assertIsInstance(statement, LetStatement)
        statement = cast(LetStatement, statement)
        self.assertEqual(statement.name.value, name)
        self.assertTrue(statement.name.token_literal(), name)
        return True

    @parameterized.expand(
        [
            ("let x = 5;", "x", 5),
            ("let y = true;", "y", True),
            ("let foobar = y;", "foobar", "y"),
        ]
    )
    def test_let_statements(
        self, input: str, expected_name: str, expected_value: int | str | bool
    ):
        program = self._test_execution(input, 1)

        statement = program.statements[0]
        self.assertTrue(self._test_let_statement(statement, expected_name))
        value = cast(LetStatement, statement).value
        assert value is not None
        self.assertTrue(self._test_literal_expression(value, expected_value))


class TestReturnStatements(ParserTestCase):
    @parameterized.expand(
        [
            ("return 5;", 5),
            ("return true;", True),
            ("return foobar;", "foobar"),
        ]
    )
    def test_return_statements(self, input: str, expected_value: int | str | bool):
        program = self._test_execution(input, 1)
        statement = program.statements[0]
        return_value = cast(ReturnStatement, statement).return_value
        assert return_value is not None
        self.assertTrue(self._test_literal_expression(return_value, expected_value))


class TestIdentifierExpressions(ParserTestCase):
    def test_identifier_expressions(self):
        input = "foobar;"
        program = self._test_execution(input, 1)

        statement = program.statements[0]
        self.assertIsInstance(statement, ExpressionStatement)
        statement = cast(ExpressionStatement, statement)
        identifier = statement.expression
        self.assertIsInstance(identifier, IdentifierExpression)
        identifier = cast(IdentifierExpression, identifier)
        self.assertEqual("foobar", identifier.value)
        self.assertEqual("foobar", identifier.token_literal())


class TestIntegerLiteralExpressions(ParserTestCase):
    def test_integer_literal(self):
        input = "5;"
        program = self._test_execution(input, 1)

        statement = program.statements[0]
        self.assertIsInstance(statement, ExpressionStatement)
        statement = cast(ExpressionStatement, statement)
        literal = statement.expression
        self.assertIsInstance(literal, IntegerLiteralExpression)
        literal = cast(IntegerLiteralExpression, literal)
        self.assertEqual(5, literal.value)
        self.assertEqual("5", literal.token_literal())


class TestParsingPrefixExpressions(ParserTestCase):
    @parameterized.expand(
        [("!5", "!", 5), ("-15", "-", 15), ("!true", "!", True), ("!false", "!", False)]
    )
    def test_parsing_prefix_expressions(self, input: str, operator: str, value: int):
        program = self._test_execution(input, 1)

        statement = program.statements[0]
        self.assertIsInstance(statement, ExpressionStatement)
        statement = cast(ExpressionStatement, statement)
        expression = statement.expression
        self.assertIsInstance(expression, PrefixExpression)
        expression = cast(PrefixExpression, expression)
        self.assertEqual(operator, expression.operator)
        assert expression.right is not None
        self.assertTrue(self._test_literal_expression(expression.right, value))


class TestParsingInfixExpressions(ParserTestCase):
    @parameterized.expand(
        [
            ("5 + 5;", 5, "+", 5),
            ("5 - 5;", 5, "-", 5),
            ("5 * 5;", 5, "*", 5),
            ("5 / 5;", 5, "/", 5),
            ("5 > 5;", 5, ">", 5),
            ("5 < 5;", 5, "<", 5),
            ("5 == 5;", 5, "==", 5),
            ("5 != 5;", 5, "!=", 5),
            ("true == true", True, "==", True),
            ("true != false", True, "!=", False),
            ("false == false", False, "==", False),
        ]
    )
    def test_parsing_infix_expressions(
        self, input: str, left: int | bool, operator: str, right: int | bool
    ):
        program = self._test_execution(input, 1)

        statement = program.statements[0]
        self.assertIsInstance(statement, ExpressionStatement)
        statement = cast(ExpressionStatement, statement)
        assert statement.expression is not None
        self._test_infix_expression(statement.expression, left, operator, right)


class TestOperatorPrecedenceParsing(ParserTestCase):
    @parameterized.expand(
        [
            ("-a * b", "((-a) * b)"),
            ("!-a", "(!(-a))"),
            ("a + b + c", "((a + b) + c)"),
            ("a + b - c", "((a + b) - c)"),
            ("a * b * c", "((a * b) * c)"),
            ("a * b / c", "((a * b) / c)"),
            ("a + b / c", "(a + (b / c))"),
            ("a + b * c + d / e - f", "(((a + (b * c)) + (d / e)) - f)"),
            ("3 + 4; -5 * 5", "(3 + 4)((-5) * 5)"),
            ("5 > 4 == 3 < 4", "((5 > 4) == (3 < 4))"),
            ("5 < 4 != 3 > 4", "((5 < 4) != (3 > 4))"),
            ("3 + 4 * 5 == 3 * 1 + 4 * 5", "((3 + (4 * 5)) == ((3 * 1) + (4 * 5)))"),
            ("true", "true"),
            ("false", "false"),
            ("3 > 5 == false", "((3 > 5) == false)"),
            ("3 < 5 == true", "((3 < 5) == true)"),
            ("1 + (2 + 3) + 4", "((1 + (2 + 3)) + 4)"),
            ("(5 + 5) * 2", "((5 + 5) * 2)"),
            ("2 / (5 + 5)", "(2 / (5 + 5))"),
            ("-(5 + 5)", "(-(5 + 5))"),
            ("!(true == true)", "(!(true == true))"),
            ("a + add(b * c) + d", "((a + add((b * c))) + d)"),
            (
                "add(a, b, 1, 2 * 3, 4 + 5, add(6, 7 * 8))",
                "add(a, b, 1, (2 * 3), (4 + 5), add(6, (7 * 8)))",
            ),
            ("add(a + b + c * d / f + g)", "add((((a + b) + ((c * d) / f)) + g))"),
        ]
    )
    def test_operator_precedence_parsing(self, input: str, expected: str):
        program = self._test_execution(input)
        self.assertEqual(expected, str(program))


class TestBooleanLiteralExpressions(ParserTestCase):
    @parameterized.expand([("true", True), ("false", False)])
    def test_boolean_literal_expressions(self, input, expected: bool):
        program = self._test_execution(input, 1)

        statement = program.statements[0]
        self.assertIsInstance(statement, ExpressionStatement)
        statement = cast(ExpressionStatement, statement)
        assert statement.expression is not None
        self._test_boolean_literal(statement.expression, expected)


class TestIfExpressions(ParserTestCase):
    def test_if_expression(self):
        input = "if (x < y) { x }"
        program = self._test_execution(input, 1)

        statement = program.statements[0]
        self.assertIsInstance(statement, ExpressionStatement)
        statement = cast(ExpressionStatement, statement)
        expression = statement.expression
        self.assertIsInstance(expression, IfExpression)
        expression = cast(IfExpression, expression)
        self.assertTrue(
            self._test_infix_expression(expression.condition, "x", "<", "y")
        )
        self.assertEqual(1, len(expression.consequence.statements))
        consequence = expression.consequence.statements[0]
        self.assertIsInstance(consequence, ExpressionStatement)
        consequence = cast(ExpressionStatement, consequence)
        self.assertTrue(self._test_identifier_literal(consequence.expression, "x"))
        self.assertIsNone(expression.alternative)

    def test_if_else_expression(self):
        input = "if (x < y) { x } else { y }"
        program = self._test_execution(input, 1)

        statement = program.statements[0]
        self.assertIsInstance(statement, ExpressionStatement)
        statement = cast(ExpressionStatement, statement)
        expression = statement.expression
        self.assertIsInstance(expression, IfExpression)
        expression = cast(IfExpression, expression)
        self.assertTrue(
            self._test_infix_expression(expression.condition, "x", "<", "y")
        )
        self.assertEqual(1, len(expression.consequence.statements))
        consequence = expression.consequence.statements[0]
        self.assertIsInstance(consequence, ExpressionStatement)
        consequence = cast(ExpressionStatement, consequence)
        self.assertTrue(self._test_identifier_literal(consequence.expression, "x"))
        self.assertEqual(1, len(expression.alternative.statements))
        alternative = expression.alternative.statements[0]
        self.assertIsInstance(alternative, ExpressionStatement)
        alternative = cast(ExpressionStatement, alternative)
        self.assertTrue(self._test_identifier_literal(alternative.expression, "y"))


class TestFunctionLiteralExpressions(ParserTestCase):
    def test_function_literal_parsing(self):
        input = "fn(x, y) { x + y; }"
        program = self._test_execution(input, 1)

        statement = program.statements[0]
        self.assertIsInstance(statement, ExpressionStatement)
        statement = cast(ExpressionStatement, statement)
        expression = statement.expression
        self.assertIsInstance(expression, FunctionLiteralExpression)
        expression = cast(FunctionLiteralExpression, expression)
        self.assertEqual(2, len(expression.parameters))
        self.assertTrue(self._test_literal_expression(expression.parameters[0], "x"))
        self.assertTrue(self._test_literal_expression(expression.parameters[1], "y"))
        self.assertEqual(1, len(expression.body.statements))
        body = expression.body.statements[0]
        self.assertIsInstance(body, ExpressionStatement)
        body = cast(ExpressionStatement, body)
        self.assertTrue(self._test_infix_expression(body.expression, "x", "+", "y"))

    @parameterized.expand(
        [
            ("fn() {}", []),
            ("fn(x) {}", ["x"]),
            ("fn(x, y, z) {}", ["x", "y", "z"]),
        ]
    )
    def test_function_parameter_parsing(self, input: str, expectedParams: list[str]):
        program = self._test_execution(input, 1)

        statement = program.statements[0]
        self.assertIsInstance(statement, ExpressionStatement)
        statement = cast(ExpressionStatement, statement)
        expression = statement.expression
        self.assertIsInstance(expression, FunctionLiteralExpression)
        expression = cast(FunctionLiteralExpression, expression)
        self.assertEqual(len(expectedParams), len(expression.parameters))
        for i, expected in enumerate(expectedParams):
            self.assertTrue(
                self._test_literal_expression(expression.parameters[i], expected)
            )


class TestCallExpressionParsing(ParserTestCase):
    def test_call_expression_parsing(self):
        input = "add(1, 2 * 3, 4 + 5);"
        program = self._test_execution(input, 1)

        statement = program.statements[0]
        self.assertIsInstance(statement, ExpressionStatement)
        statement = cast(ExpressionStatement, statement)
        expression = statement.expression
        self.assertIsInstance(expression, CallExpression)
        expression = cast(CallExpression, expression)
        self.assertTrue(self._test_identifier_literal(expression.function, "add"))
        self.assertEqual(3, len(expression.arguments))
        self.assertTrue(self._test_literal_expression(expression.arguments[0], 1))
        self.assertTrue(self._test_infix_expression(expression.arguments[1], 2, "*", 3))
        self.assertTrue(self._test_infix_expression(expression.arguments[2], 4, "+", 5))
