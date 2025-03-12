import fitz  # PyMuPDF
from pathlib import Path
import shutil

def is_pdf_corrupted(pdf_path):
    try:
        #TODO:: password protected pdf separate
        with fitz.open(pdf_path) as doc:
            if doc.page_count < 1:
                return True  # PDF opened, but contains no pages
        return False
    except Exception as e:
        print(f"Error: {e}")
        return True  # Error indicates corruption


# Set the starting directory
start_dir = Path(r"X:\FIXVERSION\iCloud\pdf")

# Ensure the "corrupted_pdf" folder exists
corrupted_folder = start_dir / "corrupted_pdf"
corrupted_folder.mkdir(exist_ok=True)

# Recursively find all pdf files
pdf_files = list(start_dir.rglob('*.pdf'))

for pdf_file in pdf_files:
    print(f"{pdf_file}")
    if is_pdf_corrupted(pdf_file):
        print("The PDF file is corrupted.")
        try:
            #TODO check for existing, don't overwrite!
            shutil.move(pdf_file, corrupted_folder / pdf_file.name)
        except Exception as e:
            print(f"Error moving {pdf_file}: {e}")
            continue
print("Done")