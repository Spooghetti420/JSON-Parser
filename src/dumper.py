from typing import Union


def indent_by(text: str, amount: int):
    return (" " * amount) + text


def __dump(json: Union[dict, list], indent=0) -> str:
    output = ""
    if isinstance(json, dict):
        output += "{\n"  # Opening bracket
        output += ",\n".join(indent_by(f'"{key}": {__dump(value, indent+4)}', indent+4) for key, value in json.items())  # Keys and values
        output += "\n" + " " * indent + "}"  # Closing bracket
    elif isinstance(json, list):
        output += "[" + ", ".join(__dump(value, indent) for value in json) + "]"
    elif isinstance(json, (int, float)):
        output += str(json)
    elif isinstance(json, str):
        output += f'"{json}"'
    elif isinstance(json, bool):
        output += str(json).lower()
    elif json is None:
        output += "null"
    
    return output


def main():
    from jparser import parse
    from tokeniser import tokenise
    with open(r".\json\example1.json") as f:
        content = f.read()
        json = parse(tokenise(content))
    
    output: str = __dump(json)
    with open("file_out.json", mode="w") as out_file:
        out_file.write(output)


if __name__ == "__main__":
    main()