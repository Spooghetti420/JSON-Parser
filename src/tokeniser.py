from math import floor
from typing import Any, Callable, Optional
from tokens import Token, TokenTypes


class JSONTokenError(ValueError):
    pass

def __tokenise(json_str: str):
    current: int = 0
    start: int = 0
    line: int = 0
    tokens: list[Token] = []

    def at_end():
        return current >= len(json_str)

    def is_num(x: str) -> bool:
        return "0" <= x <= "9"

    def is_letter(x: str) -> bool:
        return "A" <= x <= "z"

    def add_token(token_type: TokenTypes, literal: Optional[Any] = None):
        nonlocal start
        tokens.append(Token(current, token_type, json_str[start:current], literal))
        start = current

    def subsume(value_type: Callable, limit: int = None) -> str:
        nonlocal current
        output = ""
        i = 0
        while value_type((t := json_str[current])) and (((limit is not None) and i < limit) or limit is None):
            output += t
            current += 1

        return output

    def consume_until(end_value: str) -> None:
        # Continually increments `current` until it is equal to the given "end value".
        nonlocal current
        while json_str[current:current+len(end_value)] != end_value:
            current += 1
        return

            
    def parse_string() -> str:
        """Given a starting quotation mark, finds an ending quotation mark and the contained text."""
        nonlocal current
        content = ""

        while not at_end():
            t = json_str[current]
            if t == "\\":
                try:
                    current += 1
                    next_t = json_str[current]
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
                        next_four = json_str[current+1:current+5]
                        current += 4
                        if len(next_four) != 4:
                            raise IndexError()
                        content += bytes(next_four, "ascii").decode("unicode-escape")

                except IndexError:
                    # print(f"String abruptly terminated at {line} col {start}")
                    raise SystemExit(1)

            elif t == '"':
                current += 1
                return content
            else:
                content += t

            current += 1
    
    def parse_num() -> float:
        nonlocal current
        current -= 1

        content = "" # String representation of the number being parsed
        
        content += subsume(is_num) # Add a series of numbers to the string
        decimal = subsume(lambda x: x == ".", limit=1) # Potentially add a decimal point to the string
        if decimal != "":
            content += decimal
            fractional_part = subsume(is_num) # If decimal part exists, find any fractional part after the point
            content += fractional_part

        # Try to find an 'e' for exponential notation
        e = subsume(lambda x: x == "e", limit=1)
        if e != "":
            content += "e"
            sign = subsume(lambda s: s in ("+", "-"), limit=1)
            content += sign
            exponent = subsume(is_num)
            if exponent:
                content += exponent
            else:
                raise JSONTokenError(f"Number literal {json_str[start:current+1]} contains exponent notation with invalid or absent subsequent exponent.")
        
        num_float = float(content)
        if floor(num_float) - num_float < 1e-6:
            return int(num_float)
        else:
            return num_float

    # Tokenising begins here
    while not at_end():
        t = json_str[current]
        current += 1

        if t.isspace():
            if t == "\n":
                line += 1
            start = current
        elif t == "{":
            add_token(TokenTypes.LEFT_CURLY_BRACKET)
        elif t == "}":
            add_token(TokenTypes.RIGHT_CURLY_BRACKET)
        elif t == "[":
            add_token(TokenTypes.LEFT_SQUARE_BRACKET)
        elif t == "]":
            add_token(TokenTypes.RIGHT_SQUARE_BRACKET)
        elif t == ",":
            add_token(TokenTypes.COMMA)
        elif t == ":":
            add_token(TokenTypes.COLON)
        elif t == '"':
            add_token(TokenTypes.STRING, parse_string())
        elif is_num(t):
            add_token(TokenTypes.NUMBER, parse_num())
        elif t == "/":
            if json_str[current] == "/":
                # We have a comment; these are not permitted in JSON, but I want to include them!
                consume_until("\n")
                current += 1
            elif json_str[current] == "*":
                # Multiline comment, in fact!
                consume_until("*/")
                current += 1
        elif is_letter(t):
            current -= 1
            word = subsume(is_letter)
            if word == "true":
                add_token(TokenTypes.TRUE, True)
            elif word == "false":
                add_token(TokenTypes.FALSE, False)
            elif word == "null":
                add_token(TokenTypes.NULL, None)

    add_token(TokenTypes.EOF)

    return tokens