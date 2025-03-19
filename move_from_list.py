import os
import pickle
from pathlib import Path
import shutil
import logging
from logging.handlers import RotatingFileHandler
import datetime
import sys

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

def load_database_from_pickle(filepath):
    if os.path.exists(filepath):
        with open(filepath, 'rb') as f:
            db = pickle.load(f)
        return db
    else:
        return []
    
def get_available_subfolder(output_dir: Path, base_name: str, max_attempts: int = 500000):
    """
    Returns the first subfolder under `output_dir` (as a Path object) 
    where a file named `base_name` does not exist.
    Ensures that the subfolder is created if missing.
    Returns None after `max_attempts` if no available subfolder is found.
    """
    logger = logging.getLogger()
    
    # Start counting subfolders from 1
    for subfolder_index in range(1, max_attempts):
        subfolder_path = output_dir / str(subfolder_index)
        # Ensure the subfolder exists
        subfolder_path.mkdir(parents=True, exist_ok=True)

        # Construct the candidate file path within this subfolder
        candidate_path = subfolder_path / base_name
        
        # Check if the file doesn't already exist
        if not candidate_path.exists():
            return subfolder_path

    logger.warning(f"Could not find an available subfolder after {max_attempts} attempts.")
    return None

if __name__ == '__main__':
    output_main = Path(r"X:\AppleShit\duplicates")
    c = Counter()
    logger = global_logging(output_main)
    if not output_main.exists():
        print(f"Output directory does not exist: {output_main}")
        sys.exit()
    db = load_database_from_pickle(r"X:\_SAFE\0_DATA_SAFE\Movies\database.pickle")
    if not db:
        print("Empty database")
        sys.exit()
    print(len(db))

    for entry in db:
        c.update()
        fpath = Path(entry)
        if not fpath.exists():
            print(f"Missing: {fpath}")
            logger.error(f"Missing: {fpath}")
            continue
        try:
            relative_path = fpath.relative_to(r"X:\_SAFE\0_DATA_SAFE\Movies")
        except ValueError:
            print(f"Path is not under the root directory: {fpath}")
            logger.error(f"Path is not under the root directory: {fpath}")
            continue
        destination = output_main / relative_path.parent
        subdir = get_available_subfolder(destination, fpath.name)
        if subdir:
            try:
            # Move the file in the same file system
                fpath.rename(subdir / fpath.name)
            except Exception as e:
                print(f"Could not move {fpath}: {e}")
                logger.error(f"Could not move {fpath}: {e}")
        else:
            print(f"Empty subdir {fpath}")
            logger.error(f"Empty subdir {fpath}")
    print("Done")
    c.show()
