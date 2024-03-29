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
    def __init__(self) -> None:
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
        return str(self.expression) if self.expression else ""


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


class InfixExpression(ExpressionNode):
    def __init__(
        self,
        token=Token(TokenType.ILLEGAL, ""),
        left: ExpressionNode | None = None,
        operator: str = "",
        right: ExpressionNode | None = None,
    ):
        self.token = token
        self.left = left
        self.operator = operator
        self.right = right

    def token_literal(self) -> str:
        return self.token.literal

    def __str__(self) -> str:
        return f"({str(self.left)} {str(self.operator)} {str(self.right)})"


class BooleanLiteralExpression(ExpressionNode):
    def __init__(
        self, token: Token = Token(TokenType.ILLEGAL, ""), value: bool = False
    ):
        self.token = token
        self.value = value

    def token_literal(self) -> str:
        return self.token.literal

    def __str__(self) -> str:
        return self.token.literal


class BlockStatement(StatementNode):
    def __init__(self, token: Token = Token(TokenType.ILLEGAL, "")):
        super().__init__(token)
        self.statements: list[StatementNode] = []

    def token_literal(self) -> str:
        return self.token.literal

    def __str__(self) -> str:
        return "".join(str(s) for s in self.statements)


class IfExpression(ExpressionNode):
    def __init__(
        self,
        token: Token = Token(TokenType.ILLEGAL, ""),
        condition: ExpressionNode | None = None,
        consequence: BlockStatement = BlockStatement(),
        alternative: BlockStatement | None = None,
    ):
        self.token = token
        self.condition = condition
        self.consequence = consequence
        self.alternative = alternative

    def token_literal(self) -> str:
        return self.token.literal

    def __str__(self) -> str:
        out = f"if {str(self.condition)} {str(self.consequence)}"
        if self.alternative:
            out += f" else {str(self.alternative)}"
        return out


class FunctionLiteralExpression(ExpressionNode):
    def __init__(
        self,
        token: Token = Token(TokenType.ILLEGAL, ""),
        parameters: list[IdentifierExpression] = [],
        body: BlockStatement = BlockStatement(),
    ):
        self.token = token
        self.parameters = parameters
        self.body = body

    def token_literal(self) -> str:
        return self.token.literal

    def __str__(self) -> str:
        return f"{self.token.literal}({', '.join(str(p) for p in self.parameters)}) {str(self.body)}"


class CallExpression(ExpressionNode):
    def __init__(
        self,
        token: Token = Token(TokenType.ILLEGAL, ""),
        function: ExpressionNode | None = None,
        arguments: list[ExpressionNode] = [],
    ):
        self.token = token
        self.function = function
        self.arguments = arguments

    def token_literal(self) -> str:
        return self.token.literal

    def __str__(self) -> str:
        return f"{str(self.function)}({', '.join(str(a) for a in self.arguments)})"
