from monkeypie.token import Token, TokenType, KEYWORDS


class Lexer:
    def __init__(self, input_: str):
        self._input: str = input_
        self._position: int = 0
        self._read_position: int = 0
        self._ch: str = ""

        self.read_char()

    @staticmethod
    def is_letter(ch: str) -> bool:
        return ch.isalpha() or ch == "_"

    @staticmethod
    def is_digit(ch: str) -> bool:
        return ch.isdigit()

    def read_char(self):
        if self._read_position >= len(self._input):
            self._ch = "\0"
        else:
            self._ch = self._input[self._read_position]
        self._position = self._read_position
        self._read_position += 1

    def peek_char(self) -> str:
        if self._read_position >= len(self._input):
            return "\0"
        return self._input[self._read_position]

    def read_number(self) -> str:
        position = self._position
        while self.is_digit(self._ch):
            self.read_char()
        return self._input[position : self._position]

    def read_identifier(self) -> str:
        position = self._position
        while self.is_letter(self._ch):
            self.read_char()
        return self._input[position : self._position]

    @staticmethod
    def lookup_identifier(identifier: str) -> TokenType:
        try:
            return KEYWORDS[identifier]
        except KeyError:
            return TokenType.IDENT

    def skip_whitespace(self):
        while self._ch.isspace() or self._ch in ("\t", "\n", "\r"):
            self.read_char()

    def next_token(self) -> Token:
        token: Token

        self.skip_whitespace()

        match self._ch:
            case "=":
                if self.peek_char() == "=":
                    ch: str = str(self._ch)
                    self.read_char()
                    token = Token(TokenType.EQ, ch + self._ch)
                else:
                    token = Token(TokenType.ASSIGN, self._ch)
            case ";":
                token = Token(TokenType.SEMICOLON, self._ch)
            case "(":
                token = Token(TokenType.LPAREN, self._ch)
            case ")":
                token = Token(TokenType.RPAREN, self._ch)
            case "{":
                token = Token(TokenType.LBRACE, self._ch)
            case "}":
                token = Token(TokenType.RBRACE, self._ch)
            case ",":
                token = Token(TokenType.COMMA, self._ch)
            case "+":
                token = Token(TokenType.PLUS, self._ch)
            case "-":
                token = Token(TokenType.MINUS, self._ch)
            case "!":
                if self.peek_char() == "=":
                    ch = str(self._ch)
                    self.read_char()
                    token = Token(TokenType.NOT_EQ, ch + self._ch)
                else:
                    token = Token(TokenType.BANG, self._ch)
            case "/":
                token = Token(TokenType.SLASH, self._ch)
            case "*":
                token = Token(TokenType.ASTERISK, self._ch)
            case "<":
                token = Token(TokenType.LT, self._ch)
            case ">":
                token = Token(TokenType.GT, self._ch)
            case "\0":
                token = Token(TokenType.EOF, self._ch)
            case _:
                if self.is_letter(self._ch):
                    literal = self.read_identifier()
                    return Token(self.lookup_identifier(literal), literal)
                elif self.is_digit(self._ch):
                    return Token(TokenType.INT, self.read_number())
                else:
                    token = Token(TokenType.ILLEGAL, self._ch)

        self.read_char()
        return token
