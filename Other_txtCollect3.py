from pathlib import Path
from datetime import datetime


pre_text = "A következő forrás egy hangfájl átirata, emiatt találhatók benne helyesírási és értelmezési hibák. Javítsd ki a helyesírási és értelmi hibákat. Semmiképp se hagyj ki gondolatot a forrásból, de ha találsz duplikált szavakat, vedd ki. Szabadon kiegészítheted plusz mondatokkal és bővítheted a forrást. A végén egy összefüggő, koherens szöveget alkoss. A kész szöveg elején legyen benne a Source: (fájlnév).txt sor. Adj neki címet is."

def create_file_name(input_folder,name,idx,id=0):
    output_file = input_folder / f"collection-{name}_{idx}_{id}.txt"
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

        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            continue
        print(len(content))
        if len(content)>20000:
            pieces = [content[i:i+5000] for i in range(0, len(content), 5000)]
            for id, p in enumerate(pieces):
                write_content = f"{pre_text}\n\nSource: {file_path.name} \n\n {p} \n\n\n"
                output_file = create_file_name(input_folder,file_path.name,idx,id)
                output_file.write_text(write_content, encoding="utf-8")
                print(output_file.name)
                print(len(write_content))

if __name__ == '__main__':
    input_folder = Path('/Users/gabor/Documents/chatty/proc')
    col_txt(input_folder)