# FILEPATH: /Users/vlad/Documents/dev/10clouds/aiconsole/backend/aiconsole/tests/encoding_test.toml
import random
import string


def generate_random_non_ascii_symbols(num_symbols):
    symbols: list[str] = []
    while len(symbols) < num_symbols:
        symbol = random.choice(string.printable)
        if symbol not in string.ascii_letters and symbol not in string.digits:
            symbols.append(symbol)
    return symbols


random_symbols = generate_random_non_ascii_symbols(1000)

with open("encoding_test.toml", "w") as file:
    file.write("random_symbols = " + repr(random_symbols))
