from abc import ABCMeta, abstractmethod

from monkeypie.token import Token, TokenType


class Node(metaclass=ABCMeta):
    @abstractmethod
    def token_literal(self) -> str:
        raise NotImplementedError


class StatementNode(Node, metaclass=ABCMeta):
    @abstractmethod
    def statement_node(self):
        raise NotImplementedError


class ExpressionNode(Node, metaclass=ABCMeta):
    @abstractmethod
    def expression_node(self):
        raise NotImplementedError


class ProgramNode(Node):
    def __init__(self):
        self.statements: list[StatementNode] = []

    def token_literal(self) -> str:
        return "".join([str(s) for s in self.statements])


class IdentifierExpression(Node):
    def __init__(self, token=Token(TokenType.ILLEGAL, ""), value=""):
        self.token = token
        self.value = value

    def token_literal(self) -> str:
        return self.token.literal


class LetStatement(StatementNode):
    def __init__(
        self,
        token: Token = Token(TokenType.ILLEGAL, ""),
        name: IdentifierExpression = IdentifierExpression(),
        value: ExpressionNode | None = None,
    ):
        self.token = token
        self.name = name
        self.value = value

    def statement_node(self):
        pass

    def token_literal(self) -> str:
        if not self.token:
            return ""
        return self.token.literal


class ReturnStatement(StatementNode):
    def __init__(
        self,
        token=Token(TokenType.ILLEGAL, ""),
        return_value: ExpressionNode | None = None,
    ):
        self.token = token
        self.return_value = return_value

    def statement_node(self):
        pass

    def token_literal(self) -> str:
        if not self.token:
            return ""
        return self.token.literal
