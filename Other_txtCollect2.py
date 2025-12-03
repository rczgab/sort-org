from pathlib import Path
from datetime import datetime


pre_text = "A következő forrás egy hangfájl átirata, emiatt találhatók benne helyesírási és értelmezési hibák. Javítsd ki a helyesírási és értelmi hibákat. Semmiképp se hagyj ki gondolatot a forrásból, de ha találsz duplikált szavakat, vedd ki. Szabadon kiegészítheted plusz mondatokkal és bővítheted a forrást. A végén egy összefüggő, koherens szöveget alkoss. A kész szövegben legyen benne a Source: (fájlnév).txt sor."

def create_file_name(input_folder,name,idx):
    output_file = input_folder / f"collection-{name}_{idx}.txt"
    return output_file

def col_txt(input_folder):
    # Create output file name with current datetime
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    # Get sorted list of txt files in increasing order by name.
    txt_files = sorted(input_folder.glob("*.txt"))
    max_chars = 100000
    write_content = ""

    for idx, file_path in enumerate(txt_files):
        # Skip the collection file if it exists in the folder.
        if file_path.name.startswith("collection-") and file_path.name.endswith(".txt"):
            continue

        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            continue

        write_content = f"{pre_text}\n\nSource: {file_path.name} \n\n {content} \n\n\n"

        if len(write_content) > max_chars:
            print("Exceeding file limit by itself!!")

        output_file = create_file_name(input_folder,file_path.name,idx)
        output_file.write_text(write_content, encoding="utf-8")
        print(output_file.name)
        print(len(write_content))

if __name__ == '__main__':
    input_folder = Path('/Users/gabor/Documents/VoiceToTranscript_family')
    col_txt(input_folder)