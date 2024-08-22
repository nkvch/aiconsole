from pathlib import Path
import toml
import requests


def load_toml_files(directory: str):
    absolute_directory = Path(directory).resolve()
    print(f"Searching for TOML files in: {absolute_directory}")

    toml_data = []
    toml_files_found = list(Path(directory).glob('*.toml'))

    if not toml_files_found:
        print("No TOML files found in the directory.")
        return toml_data

    for toml_file in toml_files_found:
        try:
            with open(toml_file, 'r') as file:
                data = toml.load(file)
                print(f"Loaded data from {toml_file.name}: {data}")
                toml_data.append(data)
        except toml.TomlDecodeError as e:
            print(f"Error decoding TOML file {toml_file.name}: {e}")
        except Exception as e:
            print(f"Error reading TOML file {toml_file.name}: {e}")

    return toml_data

def clean_file_path(file_path: str) -> str:
    if file_path.startswith('file://'):
        file_path = file_path[7:]
    return file_path

def read_content_from_python_file(base_path: Path, file_name: str) -> str:
    file_path = base_path / file_name
    content = ""
    try:
        with open(file_path, 'r') as file:
            content = file.read()
    except Exception as e:
        print(f"Error reading Python file {file_path}: {e}")
    return content

def transform_toml_to_db_data(toml_data, base_directory: Path):
    db_data = []
    for index, item in enumerate(toml_data, start=1):
        content_file = clean_file_path(item.get("content", ""))
        if content_file and Path(content_file).suffix == '.py':
            content = read_content_from_python_file(base_directory, content_file)
        else:
            content = item.get("content", "")

        item_id = str(index)
        material_data = {
            "id": item_id,
            "name": item.get("name", "string"),
            "version": item.get("version", "0.0.1"),
            "usage": item.get("usage", "string"),
            "usage_examples": item.get("usage_examples", ["string"]),
            "defined_in": item.get("defined_in", "aiconsole"),
            "type": item.get("type", "material"),
            "default_status": item.get("default_status", "enabled"),
            "status": item.get("status", "enabled"),
            "override": item.get("override", True),
            "content_type": item.get("content_type", "static_text"),
            "content": content,
            "content_static_text": item.get("content_static_text", None)
        }
        db_data.append(material_data)
    return db_data

def post_data_to_api(data, api_base_url):
    headers = {'Content-Type': 'application/json'}
    for item in data:
        try:
            asset_id = item['id']
            url = f"{api_base_url}/api/materials/{asset_id}"
            response = requests.post(url, json=item, headers=headers)
            response.raise_for_status()
            print(f"Successfully posted data to {url}")
        except requests.exceptions.RequestException as e:
            print(f"Error posting data to API at {url}: {e}")

def main():
    toml_directory = '../../../../../aiconsole/preinstalled/materials/'
    toml_files = load_toml_files(toml_directory)

    if not toml_files:
        print("No TOML files were processed.")
        return

    api_base_url = "http://127.0.0.1:8000"

    print("Processing TOML files...")

    base_directory = Path(toml_directory).resolve()
    transformed_data = transform_toml_to_db_data(toml_files, base_directory)

    post_data_to_api(transformed_data, api_base_url)

if __name__ == "__main__":
    main()
