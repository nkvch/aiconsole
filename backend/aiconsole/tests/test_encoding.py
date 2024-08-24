try:
    with open("encoding_test.toml", "r", encoding="utf8", errors="replace") as file:
        content = file.read()
        print(content)
except FileNotFoundError:
    print("The file was not found.")
except PermissionError:
    print("Insufficient permissions to read the file.")
except UnicodeDecodeError:
    print("The file is not UTF-8 encoded.")
except UnicodeError:
    print("The file is not UTF-8 encoded.")
