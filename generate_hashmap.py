import os
import datetime
import logging
from logging.handlers import RotatingFileHandler
import sys
import exifread
import pickle
import hashlib
import shutil
from dataclasses import dataclass, field
from typing import Optional
from counter_util import Counter
from pathlib import Path

@dataclass
class FileInfo:
    name: str
    path: str
    size: int
    mtime: datetime.datetime
    hash: str = field(default="")
    exif_time: Optional[datetime.datetime] = field(default=None)

#Calculate hash files. The function is able to handle errors and return None in case of an error.
#The function is able to shorten the hash calculation to the first 100mb if the file size is greater than 1.5 Gb
#The function returns the hash value as a string
# Later the hash value is used as a key in the hash_map, and the size is checked to ensure further safety
def calc_hash(file_path, hash_algo=hashlib.sha3_256, chunk_size=65536, shorten=False):
    """Compute the hash of a file."""
    hash_obj = hash_algo()
    try:
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(chunk_size)
                #Shorten option for optional use. Code is left here for future use.
                if shorten:
                    if f.tell() > 250 * 1024 * 1024:
                        print(f"Shortening (250mb) hash calculation for {file_path}")
                        break
                if not chunk:
                    break
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
    except Exception as e:
        print(f"Error hashing file {file_path}: {e}")
        return None
    

    #Crawler
#Crawls through the directory and yields the file information
#The function is recursive
#The function is able to handle permission errors and file not found errors
def crawler(root_directory, file_extensions = None):

    #Set logger
    logger = logging.getLogger()
    try:
        with os.scandir(root_directory) as entries:
            for entry in entries:
                if entry.is_dir(follow_symlinks=False):
                    yield from crawler(entry.path, file_extensions)
                elif entry.is_file(follow_symlinks=False):
                    if file_extensions is None or entry.name.lower().endswith(file_extensions):
                    # Access file information using DirEntry
                        file_info = FileInfo(
                            name = entry.name,
                            path = entry.path,
                            size = entry.stat().st_size,
                            mtime = datetime.datetime.fromtimestamp(entry.stat().st_mtime)
                            #'ctime': datetime.datetime.fromtimestamp(entry.stat().st_ctime),
                        )
                        yield file_info
    except FileNotFoundError as e:
        print(f"Directory not found: {root_directory}", exc_info=True)
    except PermissionError as e:
        print(f"Permission denied: {root_directory}", exc_info=True)
    except Exception as e:
        print(f"Unexpected error in crawler: {e}", exc_info=True)
    
#Save database in a pickle file
def save_database_to_pickle(db, filepath):
    with open(filepath, 'wb') as f:
        pickle.dump(db, f)

if __name__ == "__main__":

    root_dir = Path("C:/Users/G/Pictures/Wallp")
    count = Counter()
    pathMap = {}
    hashMap = {}

    print(f"Crawl started: {root_dir}")

    for file_info in crawler(root_dir):
        count.update()
        file_info.hash = calc_hash(file_info.path)
        pathMap[file_info.path] = file_info
    count.show()
    print('Crawl ended.')
    filename = f"{root_dir.name}pathmap.pkl"
    mpath = root_dir / filename

    save_database_to_pickle(pathMap,mpath)

