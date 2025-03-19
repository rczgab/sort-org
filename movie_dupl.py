from pathlib import Path
import hashlib
import logging
from logging.handlers import RotatingFileHandler
import os
import datetime
import shutil
import pickle

# --- Helper functions ---
#Counter funtion class
class Counter:
    def __init__(self):
        self.cr = 0

    def update(self):
        self.cr += 1
        if self.cr%500 == 0:
            print(f"Feldolgozott fájlok száma: {self.cr}")

    def clear(self):
        self.cr = 0

    def show(self):
        print(f"Elemszám: {self.cr}")
#Logger
#Global logging, with a rotating file handler
#The log file is named after the current date and time
#The log file is saved in the output_main directory
def global_logging(output_main):
    # Ensure log directory exists
    os.makedirs(output_main, exist_ok=True)
    now_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_path = os.path.normpath(os.path.join(output_main, now_str + '_app.log'))

    # Create the root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # Capture all levels of logs

    if not logger.hasHandlers():
        # Define formatters
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
        # Create handlers
        log_handler = RotatingFileHandler(
            log_path, maxBytes=30 * 1024 * 1024, backupCount=100, encoding='utf-8'
        )
        log_handler.setFormatter(formatter)
        log_handler.setLevel(logging.DEBUG)
    
        # Add handler to the logger
        logger.addHandler(log_handler)

    return logger
#Calculate hash files. The function is able to handle errors and return None in case of an error.
#The function is able to shorten the hash calculation to the first 100mb if the file size is greater than 1.5 Gb
#The function returns the hash value as a string
# Later the hash value is used as a key in the hash_map, and the size is checked to ensure further safety
def calc_hash(file_path, hash_algo=hashlib.sha3_256, chunk_size=65536, shorten=False):
    logger = logging.getLogger()
    """Compute the hash of a file."""
    hash_obj = hash_algo()
    try:
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(chunk_size)
                #Shorten option for optional use. Code is left here for future use.
                if shorten:
                    if f.tell() > 10 * 1024 * 1024:
                        logger.warning(f"Shortening (250mb) hash calculation for {file_path}")
                        break
                if not chunk:
                    break
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
    except Exception as e:
        logger.warning(f"Error hashing file {file_path}: {e}")
        return None
    
def save_db(file_db, output_file):
    with open(output_file, 'w',encoding="utf-8") as f:
        for ext, size in file_db.items():
            f.write(f'{ext}\n')
            for key, value in size.items():
                if len(value) > 1:
                    f.write(f'\t{key}\n')
                    for file in value:
                        f.write(f'\t\t{file}\n')

def get_folder_priority(path: Path) -> int:
    """
    Assign priorities based on directory name in the path:
      3 = kinetorold
      2 = newarrivals
      1 = dupes
      0 = none of the above
    """
    parts = [part.lower() for part in path.parts]
    if 'kinetorold' in parts:
        return 3
    elif 'newarrivals' in parts:
        return 2
    elif 'dupes' in parts:
        return 1
    else:
        return 0
    
#Save database in a pickle file
def save_database_to_pickle(db, filepath):
    with open(filepath, 'wb') as f:
        pickle.dump(db, f)

"""
Crawl though the directory and if under the same extension and size there are more than one file, calculate the hash of them.
If the hash is the same, move the duplicates to a new directory, but leave the file which's path contains 'kinetoroldmar' as a directory in the path.
If the list of paths doesn't contain the keyword, leave the first file.
"""
if __name__ == '__main__':
    root_dir = Path(r"X:\_SAFE\0_DATA_SAFE\Movies")
    #output_main = Path(r"X:\AppleShit")

    logger = global_logging(root_dir)
    c = Counter()    
    d_files = {}
    hash_map = {}
    for file in root_dir.rglob('*'):
        if file.is_symlink():
            continue
        if file.is_file():
            extension = file.suffix.lower()[1:]
            file_size = file.stat().st_size
            if extension not in d_files:
                d_files[extension] = {}
            if file_size not in d_files[extension]:
                d_files[extension][file_size] = []
            d_files[extension][file_size].append(file)
            c.update()
    c.show()
    c.clear()

    for ext, size_dict in d_files.items():
        for size_val, file_list in size_dict.items():
              if len(file_list) > 1:
                   for file in file_list:
                        c.update()
                        hash = calc_hash(file,shorten=True)
                        if hash not in hash_map:
                            hash_map[hash] = []
                        hash_map[hash].append(file)
    c.show()
   
to_move = []  # will collect the files we want to move

for file_hash, paths_list in hash_map.items():
    if len(paths_list) <= 1:
        continue  # no duplicates here

    # 1) Calculate the folder priority of each file
    path_priorities = [(p, get_folder_priority(p)) for p in paths_list]
    # e.g. [ (Path('.../kinetorold/...'), 3), (Path('.../dupes/...'), 1), ...]

    # 2) Find the highest priority that exists in this group
    max_priority = max(pri for _, pri in path_priorities)

    # 3) Decide which files to keep vs. move
    if max_priority == 3:
        # if ANY file is in 'kinetorold', keep ALL those in kinetorold, move the rest
        keep_set = {
            p for (p, pri) in path_priorities if pri == 3
        }
    elif max_priority == 2:
        # if none in kinetorold, but some in newarrivals, keep ALL in newarrivals
        keep_set = {
            p for (p, pri) in path_priorities if pri == 2
        }
    elif max_priority == 1:
        # if only dupes is present, keep ONE in 'dupes' (the first in the list)
        dupes_only = [p for (p, pri) in path_priorities if pri == 1]
        if dupes_only:
            keep_set = {dupes_only[0]}   # or pick by whichever criteria you want
        else:
            keep_set = set()  # fallback
    else:
        # max_priority == 0, i.e. no known "special" folders
        # Requirement isn't specified for this scenario. 
        # Let's keep just the first as default:
        keep_set = {paths_list[0]}

    logger.info(f"Keeping: {keep_set}")
    # 4) Everything else is marked for moving
    for p, _ in path_priorities:
        if p not in keep_set:
            to_move.append(p)
            logger.info(f"Moving: {p}")


#Save to_move list to a file
output_file = root_dir / (f"{root_dir.name}.txt")
with open(output_file, 'w',encoding="utf-8") as f:
    for file in to_move:
        f.write(f'{file}\n')


save_database_to_pickle(to_move, root_dir / 'to_move.pkl')
print('Done')



## Now physically move them
#duplicates_folder = Path(r"X:\_SAFE\0_DATA_SAFE\Duplicates")
#duplicates_folder.mkdir(exist_ok=True)
#
#for file_path in to_move:
#    destination = duplicates_folder / file_path.name
#    print(f"Moving {file_path} -> {destination}")
#    try:
#        shutil.move(str(file_path), str(destination))
#    except Exception as e:
#        logger.error(f"Error moving {file_path}: {e}")






"""   
   
   
   # 3) Identify duplicates for each hash
    to_move = []
    for file_hash, paths_list in hash_map.items():
        if len(paths_list) <= 1:
            continue  # Not a duplicate group

        # Check if any path has 'kinetorold'
        kin_paths = [p for p in paths_list if 'kinetoroldmar' in p.parts]
        if kin_paths:
            keep_set = set(kin_paths)
        else:
            # If no 'kinetorold', we keep the *first* file in the list
            # (you might define "first" by sort, or just the first in paths_list)
            keep_set = {paths_list[0]}
        logger.info(f"Keeping: {keep_set}")
        # Move all others to duplicates folder
        for p in paths_list:
            if p not in keep_set:
                to_move.append(p)
                logger.info(f"Moving: {p}")
        print(len(to_move))

    # 5) Save database summary
    #out_file = root_dir / f"{root_dir.name}.txt"
    #save_db(d_files, out_file)
    #print("Script completed.")
                



    #for ext, size in d_files.items():
    #    print(extension)
    #    for key, value in size.items():
    #        if len(value) > 1:
    #            print(f'\t{key}')
    #            for file in value:
    #                print(f'\t\t{file}')

    #output_file = root_dir / (f"{root_dir.name}.txt")
    #save_db(d_files, output_file)
    #print('Done')"
    ""
    pass
    
    """
   