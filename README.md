# JSON Parser 
This is a JSON parser written wholly in Python which seeks to recreate the same functionality of the built-in
`json` module through home-made means.
The project more or less reflects the JSON specification (although I allowed comments in my rendition here :P) using relatively few complex concepts:
the general strategy I employ is to first tokenise the JSON file (this is extremely easy, as normal JSON requires practically no lookahead),
and then subsequently parse the generated tokens. This provides a fairly easy pathway for simplifying the work required into two stages,
wherein the tokenising phase dramatically abstracts the string data into more meaningful and interpretable chunks for the parser to grapple with.
The parsing of most objects is done by the parser, but the tokeniser handles parsing `string` and `number` literals.
I believe the grammar employed by both is a regular grammar, as we do not use e.g. productions as we would in context-free grammars.

## Use
There is likely not much use in this library, as a superior alternative in the `json` standard library exists. However, if you perchance
wish to make use of it, then simply import `myjson.py` and make use of one of two functions: `dumps` or `reads`.
I have kindly recycled the same-old confusing naming convention from the standard library to make you question what exactly
the function is `dumps`ing and why that's any different to mere `dump` :') (although in mine there is only `dumps`).

## Bugs
There are likely gazillions upon squillions of bugs that lie within this appallingly bodged "codebase", so as I'm refactoring this monstrosity,
I may or may not end up discovering them, but should I fail, please report any you find on here.