from jparser import parse
from tokeniser import tokenise
from dumper import dump

"""
This module serves as a frontend for "users" of the API.
If you wish to use this library rather than the standard
`json` library, please use the below methods instead of invoking
`dump`, `tokenise`, or `parse` directly.
"""

def loads(json_str: str) -> dict:
    """Generates a dictionary from a JSON string."""
    return parse(tokenise(json_str))

def dumps(json_dict: dict) -> str:
    """Generates a string dump of a JSON dictionary."""
    return dump(json_dict)