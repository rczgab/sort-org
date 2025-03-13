from pathlib import Path
import subprocess
from mutagen.easyid3 import EasyID3
from pydub import AudioSegment
import hashlib
import logging
from logging.handlers import RotatingFileHandler
import os
import datetime
from dataclasses import dataclass, field
from typing import Optional
import shutil
import uuid
import pickle

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
            log_path, maxBytes=15 * 1024 * 1024, backupCount=100, encoding='utf-8'
        )
        log_handler.setFormatter(formatter)
        log_handler.setLevel(logging.DEBUG)
    
        # Add handler to the logger
        logger.addHandler(log_handler)

    return logger

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

def get_unique_filename(destination):
    """Generate a unique filename by adding a counter if needed."""
    destination = Path(destination)
    if not destination.exists():
        return destination  # No conflict, return as is

    stem, suffix = destination.stem, destination.suffix
    parent = destination.parent
    counter = 1

    # Find a unique filename (e.g., "file(1).mp3", "file(2).mp3")
    while destination.exists():
        destination = parent / f"{stem}({counter}){suffix}"
        counter += 1

    return destination

def get_audio_hash(file_path):
    logger = logging.getLogger()
    try:
        audio = AudioSegment.from_file(file_path)
        data = audio.raw_data
        return hashlib.sha3_256(data).hexdigest()
    except Exception as e:
        logger.error(f"Error processing {file_path}: {e}")
        return None
    
#Save database in a pickle file
def save_database_to_pickle(db, filepath):
    with open(filepath, 'wb') as f:
        pickle.dump(db, f)
    
if __name__ == '__main__':

    root_dir = Path(r"X:\testrun\mp3_test")
    output_dir = Path(r"X:\testrun\test_out")

    logger = global_logging(output_dir)

    hashmap = {}
    c = Counter()

    for file_path in root_dir.rglob("*.mp3"):
        c.update()
        audio_hash = get_audio_hash(file_path)
        if audio_hash is None:
            logger.error(f"Error hashing {file_path}")
            continue
        if audio_hash not in hashmap:
            hashmap[audio_hash] = []
        hashmap[audio_hash].append(file_path)
    
    
    c.clear()

    for hash, fpath in hashmap.items():
        c.update()
        if len(fpath) > 1:
            uid = uuid.uuid4()
            target_dir = output_dir / uid.hex
            target_dir.mkdir(parents=True, exist_ok=True)
            for i in fpath:
                print(f"Duplicate hash: {hash} - {i}")
                target_path = target_dir / i.name
                unique_destination = get_unique_filename(target_path)
                i.rename(unique_destination)
                print(f"Moved to {unique_destination}")
                
    save_database_to_pickle(hashmap,str(output_dir / f"{root_dir.name}.pkl"))