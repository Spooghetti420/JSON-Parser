from math import floor
from typing import Any, Callable, Optional
from jtokens import Token, TokenTypes


class JSONTokenError(ValueError):
    pass


class EscapeSequenceEnd(JSONTokenError):
    pass


class Tokeniser:
    def __init__(self, json_str: str) -> None:
        self.source = json_str
        self.current: int = 0
        self.start: int = 0
        self.line: int = 0
        self.col: int = 0
        self.tokens: list[Token] = []
        self.complete: bool = False

    SYMBOLS = {
        "{": TokenTypes.LEFT_CURLY_BRACKET,
        "}": TokenTypes.RIGHT_CURLY_BRACKET,
        "[": TokenTypes.LEFT_SQUARE_BRACKET,
        "]": TokenTypes.RIGHT_SQUARE_BRACKET,
        ",": TokenTypes.COMMA,
        ":": TokenTypes.COLON  
    }

    def at_end(self):
        return self.current >= len(self.source)

    @staticmethod
    def is_num(x: str) -> bool:
        return "0" <= x <= "9"

    @staticmethod
    def is_letter(x: str) -> bool:
        return "A" <= x <= "z"

    def add_token(self, token_type: TokenTypes, literal: Optional[Any] = None):
        self.tokens.append(Token(self.line, self.col, token_type, self.source[self.start:self.current], literal))
        self.start = self.current

    def subsume(self, value_type: Callable, limit: int = None) -> str:
        output = ""
        i = 0
        while value_type((t := self.source[self.current])) and (((limit is not None) and i < limit) or limit is None):
            output += t
            self.current += 1

        return output

    def consume_until(self, end_value: str) -> None:
        # Continually increments `current` until it is equal to the given "end value".
        while self.source[self.current:self.current+len(end_value)] != end_value:
            self.current += 1
        
        return

    def parse_string(self) -> str:
        """Given a starting quotation mark, finds an ending quotation mark and returns a string with the contained text."""
        content = ""

        while not self.at_end():
            t = self.source[self.current]
            if t == "\\":
                try:
                    self.current += 1
                    next_t = self.source[self.current]
                    if next_t in ('"', "\\", "/"):
                        content += next_t
                    elif next_t == "b":
                        content += "\b"
                    elif next_t == "f":
                        content += "\f"
                    elif next_t == "\n":
                        content += "\n"
                    elif next_t == "r":
                        content += "\r"
                    elif next_t == "t":
                        content += "\t"
                    elif next_t == "u":
                        # Unicode escape sequence expected
                        next_four = self.source[self.current+1:self.current+5]
                        self.current += 4
                        if len(next_four) != 4:
                            raise EscapeSequenceEnd(f"Escape sequence (\\u{next_four}) was triggered at the end of the JSON input with insufficient characters")
                        content += bytes(next_four, "ascii").decode("unicode-escape")

                except IndexError:
                    raise EscapeSequenceEnd("")

            elif t == '"':
                self.current += 1
                return content
            else:
                content += t

            self.current += 1

    def parse_num(self) -> float:
        self.current -= 1

        content = "" # String representation of the number being parsed
        
        content += self.subsume(self.is_num) # Add a series of numbers to the string
        decimal = self.subsume(lambda x: x == ".", limit=1) # Potentially add a decimal point to the string
        if decimal != "":
            content += decimal
            fractional_part = self.subsume(self.is_num) # If decimal part exists, find any fractional part after the point
            content += fractional_part

        # Try to find an 'e' for exponential notation
        e = self.subsume(lambda x: x == "e", limit=1)
        if e != "":
            content += "e"
            sign = self.subsume(lambda s: s in ("+", "-"), limit=1)
            content += sign
            exponent = self.subsume(self.is_num)
            if exponent:
                content += exponent
            else:
                raise JSONTokenError(f"Number literal {self.source[self.start:self.current+1]} contains exponent notation with invalid or absent subsequent exponent.")
        
        num_float = float(content)
        if floor(num_float) - num_float < 1e-6:
            return int(num_float)
        else:
            return num_float

    def tokenise(self):
        if self.complete:
            return self.tokens

        # Tokenising begins here
        while not self.at_end():
            t = self.source[self.current]
            self.current += 1

            if t.isspace():
                if t == "\n":
                    self.line += 1
                self.start = self.current
            elif t in Tokeniser.SYMBOLS:
                self.add_token(Tokeniser.SYMBOLS[t])
            elif t == '"':
                self.add_token(TokenTypes.STRING, self.parse_string())
            elif self.is_num(t):
                self.add_token(TokenTypes.NUMBER, self.parse_num())
            elif t == "/":
                if self.source[self.current] == "/":
                    # We have a comment; these are not permitted in JSON, but I want to include them!
                    self.consume_until("\n")
                    self.current += 1
                elif self.source[self.current] == "*":
                    # Multiline comment, in fact!
                    self.consume_until("*/")
                    self.current += 1
            elif self.is_letter(t):
                self.current -= 1
                word = self.subsume(self.is_letter)
                if word == "true":
                    self.add_token(TokenTypes.TRUE, True)
                elif word == "false":
                    self.add_token(TokenTypes.FALSE, False)
                elif word == "null":
                    self.add_token(TokenTypes.NULL, None)

        self.add_token(TokenTypes.EOF)

        self.complete = True
        return self.tokens
        
def __tokenise(json_str: str):
    return Tokeniser(json_str).tokenise()