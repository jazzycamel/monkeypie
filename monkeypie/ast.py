from abc import ABCMeta, abstractmethod

from monkeypie.token import Token, TokenType


class Node(metaclass=ABCMeta):
    @abstractmethod
    def token_literal(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def __str__(self) -> str:
        return ""


class StatementNode(Node, metaclass=ABCMeta):
    def __init__(self, token: Token):
        self.token = token

    def statement_node(self):
        pass

    def token_literal(self) -> str:
        return self.token.literal


class ExpressionNode(Node, metaclass=ABCMeta):
    def expression_node(self):
        pass


class ProgramNode(Node):
    def __init__(self):
        self.statements: list[StatementNode] = []

    def token_literal(self) -> str:
        return "".join([str(s) for s in self.statements])

    def __str__(self) -> str:
        return "".join(str(s) for s in self.statements)


class IdentifierExpression(ExpressionNode):
    def __init__(self, token=Token(TokenType.ILLEGAL, ""), value: str = ""):
        self.token = token
        self.value = value

    def token_literal(self) -> str:
        return self.token.literal

    def __str__(self) -> str:
        return self.value


class LetStatement(StatementNode):
    def __init__(
        self,
        token: Token = Token(TokenType.ILLEGAL, ""),
        name: IdentifierExpression = IdentifierExpression(),
        value: ExpressionNode | None = None,
    ):
        super().__init__(token)
        self.name = name
        self.value = value

    def __str__(self) -> str:
        return f"{self.token_literal()} {self.name}{' = '+str(self.value) if self.value else ''};"


class ReturnStatement(StatementNode):
    def __init__(
        self,
        token=Token(TokenType.ILLEGAL, ""),
        return_value: ExpressionNode | None = None,
    ):
        super().__init__(token)
        self.return_value = return_value

    def __str__(self) -> str:
        return f"{self.token_literal()}{' '+str(self.return_value) if self.return_value else ''};"


class ExpressionStatement(StatementNode):
    def __init__(
        self,
        token=Token(TokenType.ILLEGAL, ""),
        expression: ExpressionNode | None = None,
    ):
        super().__init__(token)
        self.expression = expression

    def __str__(self) -> str:
        return ""


class IntegerLiteralExpression(ExpressionNode):
    def __init__(self, token=Token(TokenType.ILLEGAL, ""), value: int = 0):
        self.token = token
        self.value: int = value

    def token_literal(self) -> str:
        return self.token.literal

    def __str__(self) -> str:
        return self.token.literal


class PrefixExpression(ExpressionNode):
    def __init__(
        self,
        token=Token(TokenType.ILLEGAL, ""),
        operator: str = "",
        right: ExpressionNode | None = None,
    ):
        self.token = token
        self.operator = operator
        self.right = right

    def token_literal(self) -> str:
        return self.token.literal

    def __str__(self) -> str:
        return f"({self.operator}{str(self.right)})"
