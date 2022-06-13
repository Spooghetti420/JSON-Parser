from typing import Union


# Indentation is not yet functional
def indent_by(text: str, amount: int):
    return (" " * amount) + text


def dump(json: Union[dict, list], indent=0) -> str:
    output = ""
    print(f"Indent level is {indent}")
    if isinstance(json, dict):
        output += indent_by("{" + ",\n".join(f'"{key}": {dump(value, indent+4)}' for key, value in json.items()) + "}", 0)
    elif isinstance(json, list):
        output += indent_by("[" + ", ".join(dump(value, indent+4) for value in json) + "]", 0)
    elif isinstance(json, (int, float)):
        output += indent_by(str(json), 0)
    elif isinstance(json, str):
        output += indent_by(f'"{json}"', 0)
    elif isinstance(json, bool):
        output += indent_by(str(json).lower(), 0)
    elif json is None:
        output += indent_by("null", 0)
    
    return output


def main():
    from jparser import parse
    from tokeniser import tokenise
    with open("file.json") as f:
        content = f.read()
        json = parse(tokenise(content))
    
    output = dump(json)
    with open("file_out.json", mode="w") as out_file:
        out_file.write(output)


if __name__ == "__main__":
    main()