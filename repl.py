import getpass
from typing import Final

from monkeypie.lexer import Lexer
from monkeypie.parser import Parser


PROMPT: Final[str] = ">> "
MONKEY_FACE: Final[str] = r'''
           __,__
  .--.  .-"     "-.  .--.
 / .. \/  .-. .-.  \/ .. \
| |  '|  /   Y   \  |'  | |
| \   \  \ 0 | 0 /  /   / |
 \ '- ,\.-"""""""-./, -' /
  ''-' /_   ^ ^   _\ '-''
      |  \._   _./  |
      \   \ '~' /   /
       '._ '-=-' _.'
          '-----'
'''


class REPL:
    @staticmethod
    def print_parser_errors(errors: list[str]) -> None:
        print(MONKEY_FACE)
        print("Woops! We ran into some monkey business here!")
        print(" parser errors:")
        for error in errors:
            print("\t" + error)

    @staticmethod
    def start_repl() -> None:
        while True:
            line = input(PROMPT)
            lexer = Lexer(line)
            parser = Parser(lexer)
            program = parser.parse_program()
            if len(errors := parser.errors()):
                REPL.print_parser_errors(errors)
                continue

            print(program)


if __name__ == "__main__":
    print(f"Hello {getpass.getuser()}! This is the monkey programming language!")
    print("Feel free to type commands (Ctrl+C to quit)")

    try:
        REPL.start_repl()
    except KeyboardInterrupt:
        pass
