from pathlib import Path
import json

def save_db(file_db, output_file):
    with open(output_file, 'w',encoding="utf-8") as f:
        for ext, size in file_db.items():
            f.write(f'{ext}\n')
            for key, value in size.items():
                if len(value) > 1:
                    f.write(f'\t{key}\n')
                    for file in value:
                        f.write(f'\t\t{file}\n')

if __name__ == '__main__':
    root_dir = Path(r"X:\_SAFE\0_DATA_SAFE\Movies\Singles")
    
    d_files = {}
    for file in root_dir.rglob('*'):
        if file.is_symlink():
            continue
        if file.is_file():
            extension = file.suffix.lower()[1:]
            if extension not in d_files:
                d_files[extension] = {}
            if file.stat().st_size not in d_files[extension]:
                d_files[extension][file.stat().st_size] = []
            d_files[extension][file.stat().st_size].append(file)
    
    #for ext, size in d_files.items():
    #    print(extension)
    #    for key, value in size.items():
    #        if len(value) > 1:
    #            print(f'\t{key}')
    #            for file in value:
    #                print(f'\t\t{file}')

    output_file = root_dir / (f"{root_dir.name}.txt")
    save_db(d_files, output_file)
    print('Done')