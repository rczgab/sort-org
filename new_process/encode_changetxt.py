import chardet
from pathlib import Path
import shutil

def detect_encoding(file_path):
    with file_path.open('rb') as file:
        raw_data = file.read()
    detection = chardet.detect(raw_data)
    return detection['encoding'], detection['confidence']

def convert_file_to_utf8(file_path, min_confidence=0.5):
    encoding, confidence = detect_encoding(file_path)

    if encoding is None or confidence < min_confidence:
        print(f"Skipped (undetectable encoding): {file_path}")
        return

    if encoding.lower() == 'utf-8':
        print(f"Skipped (already UTF-8): {file_path}")
        return

    try:
        with file_path.open('r', encoding=encoding) as file:
            content = file.read()
        
        backup_path = file_path.with_suffix(file_path.suffix + ".bak")
        shutil.copy2(file_path, backup_path)  # Create a backup before overwriting

        with file_path.open('w', encoding='utf-8') as file:
            file.write(content)

        print(f"Converted: {file_path} from {encoding} (confidence: {confidence:.2f}) to UTF-8")

        backup_path.unlink()  # Remove the backup file after successful conversion

    except Exception as e:
        print(f"Failed to convert {file_path}: {e}")

def convert_folder_to_utf8(root_folder, file_extensions=None):
    folder_path = Path(root_folder)

    if file_extensions is None:
        print('file_extensions is None, skip')
        return

    for file_path in folder_path.rglob('*'):
        if file_path.is_file() and (file_path.suffix.lower() in file_extensions):
            convert_file_to_utf8(file_path)

if __name__ == "__main__":
    # Replace this path with your actual folder path
    folder_to_scan = Path(r"/path/to/your/folder")

    # File extensions you want to process (optional but recommended)
    extensions = {'.txt', '.py', '.csv', '.html', '.md', '.json', '.xml', '.log', '.htm'}

    convert_folder_to_utf8(folder_to_scan, extensions)
