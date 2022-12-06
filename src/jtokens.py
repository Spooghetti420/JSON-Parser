from dataclasses import dataclass
from enum import Enum, auto
from typing import Any

class TokenTypes(Enum):
    LEFT_CURLY_BRACKET = auto()
    RIGHT_CURLY_BRACKET = auto()
    COMMA = auto()
    COLON = auto()
    LEFT_SQUARE_BRACKET = auto()
    RIGHT_SQUARE_BRACKET = auto()
    
    TRUE = auto()
    FALSE = auto()
    NULL = auto()
    STRING = auto()
    NUMBER = auto()

    EOF = auto()

@dataclass
class Token:
    # start: int
    line: int
    col: int
    ttype: TokenTypes
    lexeme: str
    literal: Any

    def is_literal(self):
        for tt in (TokenTypes.STRING, TokenTypes.NUMBER, TokenTypes.NULL, TokenTypes.TRUE, TokenTypes.FALSE):
            if self.ttype is tt:
                return True
        return False

    def __repr__(self) -> str:
        return self.ttype.name + (f" ({self.literal})" if self.literal is not None else "")