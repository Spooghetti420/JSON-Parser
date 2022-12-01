from jparser import parse
from tokeniser import tokenise
from dumper import dump
import pprint


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

def loadf(file_path: str) -> dict:
    """Generates a dictionary from a file on the filesystem."""
    with open(file_path, encoding="utf-8") as json_file:
        return parse(tokenise(json_file.read()))

def dumpf(json_dict: dict, file_path: str) -> None:
    """Dumps the contents of a dictionary with JSON data into a file."""
    with open(file_path, mode="w", encoding="utf-8") as json_file:
        json_file.write(dumps(json_dict))

if __name__ == "__main__":
    example1, example2, example3, example4, example5 = loadf("json/example1.json"), loadf("json/example2.json"), loadf("json/example3.json"), loadf("json/example4.json"), loadf("json/example5.json")