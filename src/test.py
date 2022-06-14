import unittest
import os.path
import json
import myjson

from typing import Tuple


def generate_dictionaries_from_json(example_num: int) -> Tuple[dict, dict]:
    """
    Generates two dictionaries: the first is one generated from my JSON parser implementation,
    whereas the second is the builtin `json` library's result from the same file.
    The `example_num` parameter corresponds to a file name in the `json` folder in this
    directory, which contains files like `example1.json`, `example2.json`, etc.
    """
    file_path = os.path.join("json", f"example{example_num}.json")
    try:
        with open(file_path) as json_file:
            content = json_file.read()
    except FileNotFoundError:
        print(f"Error: file does not exist: {file_path}")
        raise SystemExit(1)
    
    return myjson.loads(content), json.loads(content)

class TestAllJSONsEquivalent(unittest.TestCase):
    def perform_assertion(self, number: int) -> None:
        self.assertEqual(*generate_dictionaries_from_json(number))

    def test_example1(self):
        self.perform_assertion(1)

    def test_example2(self):
        self.perform_assertion(2)

    def test_example3(self):
        self.perform_assertion(3)

    def test_example4(self):
        self.perform_assertion(4)

    def test_example5(self):
        self.perform_assertion(5)

