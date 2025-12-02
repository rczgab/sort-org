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
        if self.cr%50 == 0:
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
                    if f.tell() > 150 * 1024 * 1024:
                        #logger.warning(f"Shortening (250mb) hash calculation for {file_path}")
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

# get folder priority rank from a custom list.
def get_priority_rank(path: Path, priority_folders: list) -> int:
    """
    Check the path parts against the priority_folders list.
    Returns the index (rank) where 0 is highest priority.
    If none of the folders is found, returns len(priority_folders).
    """
    parts = [part.lower() for part in path.parts]
    for idx, folder in enumerate(priority_folders):
        if folder.lower() in parts:
            return idx
    return len(priority_folders)
    
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
    root_dir = Path(r"X:\Collection_Storage\Game")
    alternate_dir_1 = Path(r"X:\_SAFE\0_DATA_SAFE\SW_iCloudZip\localGame")
    alternate_dir_2 = Path(r"")
    alternate_dir_3 = Path(r"")

    directories = [root_dir, alternate_dir_1, alternate_dir_2, alternate_dir_3]
    
    # Define the priority folders list (order matters: first is highest)
    PRIORITY_FOLDERS = ["Collection_Storage", "local"]

    # Filter for files (optional)
    #file_filter = ('.jpg','.png','.srt','.txt','.ac3','.zip','.pam','.ass','.sfv')
    #file_filter = ('.jpg', '.jpeg')
    file_filter = ('.img',)

    logger = global_logging(root_dir.parent)
    c = Counter()    
    d_files = {}
    hash_map = {}
    for dir in directories:
        if dir == Path(r""):
            continue
        for file in dir.rglob('*'):
            if file.suffix.lower() not in file_filter:
                continue
            if file.is_symlink():
                continue
            if file.is_file():
                extension = file.suffix.lower()[1:]
                file_size = file.stat().st_size
                d_files.setdefault(extension, {}).setdefault(file_size, []).append(file)
                c.update()
        c.show()
        c.clear()

    for ext, size_dict in d_files.items():
        for size_val, file_list in size_dict.items():
              if len(file_list) > 1:
                   for file in file_list:
                        c.update()
                        hash = calc_hash(file, shorten=False)
                        if hash:
                            hash_map.setdefault(hash, []).append(file)
                        else:
                            logger.error(f"Hash empty! {file}")
    c.show()
   
to_move = []  # will collect the files we want to move

for file_hash, paths_list in hash_map.items():
    if len(paths_list) <= 1:
        continue  # no duplicates here

    # Compute the rank for each file based on the priority folders list.
    path_ranks = [(p, get_priority_rank(p, PRIORITY_FOLDERS)) for p in paths_list]
    # Find the highest priority (lowest rank number)
    best_rank = min(rank for _, rank in path_ranks)
    # Choose one file with the best rank to keep.
    candidates = [p for p, rank in path_ranks if rank == best_rank]
    keep_file = min(candidates, key=lambda p: len(str(p.parent)))
    logger.info(f"Keeping: {keep_file}")
    # Mark all other files in the group for moving.
    for p, _ in path_ranks:
        if p != keep_file:
            to_move.append(p)
            logger.info(f"Moving: {p}")

#Save to_move list to a file
output_file = root_dir.parent / (f"{root_dir.name}.txt")
with open(output_file, 'w',encoding="utf-8") as f:
    for file in to_move:
        f.write(f'{file}\n')

save_database_to_pickle(to_move, root_dir.parent / 'to_move.pkl')
   