from enum import Enum, auto
from typing import Literal
from tokeniser import __tokenise
from jtokens import Token, TokenTypes

"""WARNING: Code may not function perfectly.
    This is a module for reading in JSON files.
    It uses a simple regular grammar checking method
    to first tokenise the JSON text, whereupon a
    parser is invoked which recursively expands the
    generated tokens into an object representation of
    the JSON content.
"""

# Custom error types for more helpful error catching.
class JSONParseError(ValueError):
    pass


class JSONExpectationError(Exception):
    pass


class ParserState(Enum):
    EXPECT_KEY = auto()
    EXPECT_VALUE = auto()
    EXPECT_END = auto()


def is_literal(token: Token):
        for tt in (TokenTypes.STRING, TokenTypes.NUMBER, TokenTypes.NULL, TokenTypes.TRUE, TokenTypes.FALSE):
            if token.ttype is tt:
                return True
        return False


def parse_list(tokens: list[Token]):
        state = ParserState.EXPECT_VALUE
        output = []
        i = 0
        while i < len(tokens):
            t = tokens[i]
            if state is ParserState.EXPECT_VALUE:
                if is_literal(t):
                    output.append(t.literal)
                    try:
                        if tokens[i+1].ttype is not TokenTypes.COMMA:
                            state = ParserState.EXPECT_END
                            break
                    except IndexError:
                            state = ParserState.EXPECT_END
                            break
                elif t.ttype is TokenTypes.LEFT_SQUARE_BRACKET:
                    count = 1
                    i += 1
                    start = i
                    start_bracket, end_bracket = TokenTypes.LEFT_SQUARE_BRACKET, TokenTypes.RIGHT_SQUARE_BRACKET
                    while count > 0 and i < len(tokens):
                        t = tokens[i]
                        if t.ttype is start_bracket:
                            count += 1
                        elif t.ttype is end_bracket:
                            count -= 1
                        i += 1
                    
                    section = parse_list(tokens[start:i-1])
                    output.append(section)

                elif t.ttype is TokenTypes.LEFT_CURLY_BRACKET:
                    count = 1
                    i += 1
                    start = i
                    start_bracket, end_bracket = TokenTypes.LEFT_CURLY_BRACKET, TokenTypes.RIGHT_CURLY_BRACKET
                    while count > 0 and i < len(tokens):
                        t = tokens[i]
                        if t.ttype is start_bracket:
                            count += 1
                        elif t.ttype is end_bracket:
                            count -= 1
                        i += 1
                    
                    section = __parse(tokens[start-1:i])
                    output.append(section)

            i += 1

        return output  

def __parse(tokens: list[Token]):
    current: int = -1
    output = {}
    state = ParserState.EXPECT_KEY
    
    def at_end():
        return current >= len(tokens)

    bracket_types = {
        "[]": [TokenTypes.LEFT_SQUARE_BRACKET, TokenTypes.RIGHT_SQUARE_BRACKET],
        "{}": [TokenTypes.LEFT_CURLY_BRACKET, TokenTypes.RIGHT_CURLY_BRACKET]
    }

    def count_brackets(bracket_type: Literal["[]", "{}"]) -> int:
        count = 1
        nonlocal current
        loc_cur = current + 1

        start_bracket, end_bracket = bracket_types[bracket_type]
        while count > 0 and not at_end():
            t = tokens[loc_cur]
            if t.ttype is start_bracket:
                count += 1
            elif t.ttype is end_bracket:
                count -= 1
            loc_cur += 1

        if at_end():
            raise JSONParseError(f"{'Curly' if bracket_type == '{}' else 'Square'} bracket mismatch in JSON file starting at character {t.start}.")

        return loc_cur

    def expect(*expected_types: TokenTypes):
        nonlocal current
        current += 1
        if tokens[current].ttype not in expected_types:
            raise JSONExpectationError(f"Expected {expected_types} at {tokens[current-1].start}.")
        return tokens[current]

    expect(TokenTypes.LEFT_CURLY_BRACKET)
    while not at_end():
        t = tokens[current]

        if state is ParserState.EXPECT_KEY:
            key = expect(TokenTypes.STRING)
            expect(TokenTypes.COLON) # Expend a colon token if it exists
            try:
                value = expect(TokenTypes.STRING, TokenTypes.NUMBER, TokenTypes.NULL, TokenTypes.TRUE, TokenTypes.FALSE)
                output[key.literal] = value.literal
            except JSONExpectationError as e:
                t = tokens[current]
                if t.ttype is TokenTypes.LEFT_CURLY_BRACKET:
                    start = current
                    current = count_brackets("{}") # Find the end of this object
                    output[key.literal] = __parse(tokens[start:current])
                    current -= 1
                elif t.ttype is TokenTypes.LEFT_SQUARE_BRACKET:
                    start = current
                    current = count_brackets("[]")
                    current -= 1
                    output[key.literal] = parse_list(tokens[start+1:current])
                else:
                    raise e

            subsequent = expect(TokenTypes.COMMA, TokenTypes.RIGHT_CURLY_BRACKET)
            if subsequent.ttype is not TokenTypes.COMMA:
                break

    return output


def main():
    with open("file.json", mode="r", encoding="utf-8") as jsonf:
        tokens = __tokenise(jsonf.read())
        print(__parse(tokens))


if __name__ == "__main__":
    main()
