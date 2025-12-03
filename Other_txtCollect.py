from pathlib import Path
from datetime import datetime


"""
From a single input folder get the txt files, and collect the content of them in a single txt file.
The single txt file will be saved in the same folder as the input folder, named collection-<datetime>.txt
The txt file content should be:
- the name of the txt file
- line break
- the content of the txt file
- 2 line breaks
The collection file should not contain more than 100.000 characters.
"""

def create_file_name(input_folder,timestamp,idx):
    output_file = input_folder / f"collection-{timestamp}_{idx}.txt"
    return output_file

    
def col_txt(input_folder):
    # Create output file name with current datetime
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    # Get sorted list of txt files in increasing order by name.
    txt_files = sorted(input_folder.glob("*.txt"))
    max_chars = 100000
    write_content = ""
    collected_txt = ""
    collected = []

    for file_path in txt_files:
        # Skip the collection file if it exists in the folder.
        if file_path.name.startswith("collection-") and file_path.name.endswith(".txt"):
            continue

        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            continue

        write_content = f"Source: {file_path.name} \n\n {content} \n\n\n"

        if len(write_content) > max_chars:
            print("Exceeding file limit by itself!!")

        if len(collected_txt+write_content)>max_chars:
            collected.append(collected_txt)
            collected_txt = ""

        collected_txt += write_content

    #Store the remaining text
    collected.append(collected_txt)

    for idx, text in enumerate(collected):
        output_file = create_file_name(input_folder,timestamp,idx)
        output_file.write_text(text, encoding="utf-8")
        print(output_file.name)
        print(len(text))

if __name__ == '__main__':
    input_folder = Path('/Users/gabor/Documents/VoiceToTranscript_family')
    col_txt(input_folder)





