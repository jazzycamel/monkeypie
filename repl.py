import getpass
from typing import Final

from monkeypie.lexer import Lexer
from monkeypie.token import TokenType

PROMPT: Final[str] = ">> "


def start_repl() -> None:
    while True:
        line = input(PROMPT)
        lexer = Lexer(line)

        token = lexer.next_token()
        while token.type != TokenType.EOF:
            print(token)
            token = lexer.next_token()


if __name__ == "__main__":
    print(f"Hello {getpass.getuser()}! This is the monkey programming language!")
    print("Feel free to type commands (Ctrl+C to quit)")

    try:
        start_repl()
    except KeyboardInterrupt:
        pass
