
import os
import datetime
import logging
from logging.handlers import RotatingFileHandler
import pickle
import hashlib
import shutil
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path
import sys

# --- Constants and configuration ---

#Config



#Possible date formats for exif date extraction of images
date_formats = [
    # Basic date and time formats
    '%Y:%m:%d %H:%M:%S',       # Standard EXIF format with colons
    '%Y-%m-%d %H:%M:%S',       # Hyphenated date and time
    '%Y/%m/%d %H:%M:%S',       # Slashed date and time
    '%Y%m%d%H%M%S',           # Continuous digits for date and time
    '%d:%m:%Y %H:%M:%S',       # Day-first format with colons

    # Date-only formats
    '%Y:%m:%d',               # Date only, colon-separated
    '%Y-%m-%d',               # Date only, hyphen-separated
    '%Y/%m/%d',               # Date only, slash-separated
    '%Y%m%d',                 # Date only, continuous digits

    # Formats with milliseconds (fractional seconds)
    '%Y-%m-%d %H:%M:%S.%f',
    '%Y:%m:%d %H:%M:%S.%f',
    '%Y/%m/%d %H:%M:%S.%f',
    '%Y%m%d%H%M%S.%f',

    # Formats with timezone (using %z, no space between seconds and timezone)
    '%Y-%m-%d %H:%M:%S%z',
    '%Y:%m:%d %H:%M:%S%z',
    '%Y/%m/%d %H:%M:%S%z',
    '%Y%m%d%H%M%S%z',
    '%Y-%m-%d %H:%M:%S.%f%z',
    '%Y:%m:%d %H:%M:%S.%f%z',
    '%Y/%m/%d %H:%M:%S.%f%z',
    '%Y%m%d%H%M%S.%f%z',

    # Formats with timezone (using %Z, with space between seconds and timezone)
    '%Y-%m-%d %H:%M:%S %Z',
    '%Y:%m:%d %H:%M:%S %Z',
    '%Y/%m/%d %H:%M:%S %Z',
    '%Y%m%d%H%M%S %Z',
    '%Y-%m-%d %H:%M:%S.%f %Z',
    '%Y:%m:%d %H:%M:%S.%f %Z',
    '%Y/%m/%d %H:%M:%S.%f %Z',
    '%Y%m%d%H%M%S.%f %Z',

    # Formats with timezone (using %z, with space between seconds and timezone)
    '%Y-%m-%d %H:%M:%S %z',
    '%Y:%m:%d %H:%M:%S %z',
    '%Y/%m/%d %H:%M:%S %z',
    '%Y%m%d%H%M%S %z',
    '%Y-%m-%d %H:%M:%S.%f %z',
    '%Y:%m:%d %H:%M:%S.%f %z',
    '%Y/%m/%d %H:%M:%S.%f %z',
    '%Y%m%d%H%M%S.%f %z',

    # Additional possible formats commonly encountered in EXIF data:
    '%Y-%m-%dT%H:%M:%S',         # ISO 8601 basic (no milliseconds, no timezone)
    '%Y-%m-%dT%H:%M:%S.%f',       # ISO 8601 with fractional seconds
    '%Y-%m-%dT%H:%M:%S%z',        # ISO 8601 with timezone (no delimiter before timezone)
    '%Y-%m-%dT%H:%M:%S.%f%z',      # ISO 8601 with milliseconds and timezone
    '%Y-%m-%dT%H:%M:%S%Z',        # ISO 8601 variant with timezone abbreviation
    '%Y-%m-%dT%H:%M:%S.%f%Z',      # ISO 8601 with fractional seconds and timezone abbreviation
    '%Y%m%d_%H%M%S',             # Underscore separator between date and time
    '%Y%m%d_%H%M%S.%f',          # Underscore separator with milliseconds
    '%d-%m-%Y %H:%M:%S',         # Day-first, hyphenated date and time
    '%d/%m/%Y %H:%M:%S',         # Day-first, slashed date and time
    '%d-%m-%Y',                 # Day-first, date only with hyphens
    '%d/%m/%Y',                 # Day-first, date only with slashes
    ]
#File type to inspect, in separate divisions
image_Exif_ext = ('.jpg', '.jpeg')
image_ext = ('.png', '.gif', '.bmp', '.tif')
image_mac = ('.heic',)
video_ext = ('.mp4', '.avi', '.mov', '.mpeg','.mkv','.mts', '.mpg', '.flv', '.3gp', '.wmv','.m4v')
subscript_ext = ('.srt', '.ass')
audio_ext = ('.mp3', '.wav','.wma','.amr','.flac','.aac','.m4a')
pdf_ext = ('.pdf',)
compressed_ext = ('.zip', '.rar','.iso','.7z')
doc_ext = ('.doc','.docx','.xls','.xlsx','.txt', '.html', '.htm', '.ppt','.pptx','.xml','.csv','.rtf','.odt','.vcf','.epub','.djvu','.gp3','.gp4','.gp5','.md','.bear','.json','.dwg','.mobi')
#Merging all inspected file type
all_extensions = tuple(
    image_Exif_ext + image_ext + video_ext + subscript_ext +
    audio_ext + pdf_ext + compressed_ext + doc_ext)

#Alternative for development purposes
extension_map = {
    image_Exif_ext: 'img',
    image_ext: 'img',
    video_ext: 'video',
    subscript_ext: 'subscript',
    audio_ext: 'audio',
    pdf_ext: 'pdf',
    compressed_ext: 'compressed',
    doc_ext: 'doc',
    image_mac: 'heic'
}

def type_selector(file_info) -> str:
    for ext_tuple, label in extension_map.items():
        if file_info.name.lower().endswith(ext_tuple):
            return label
    return 'other'

    
# --- Helper functions ---
#Counter funtion class
class Counter:
    def __init__(self):
        self.cr = 0

    def update(self):
        self.cr += 1
        if self.cr%1000 == 0:
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

@dataclass
class FileInfo:
    name: str
    path: str
    size: int
    mtime: datetime.datetime
    hash: str = field(default="")
    exif_time: Optional[datetime.datetime] = field(default=None)


#Check if the variable is a year.
#The range is intentionally set to 1000-3000
def is_year(variable):
    # Try converting to an integer
    try:
        year = int(variable)
        return 1000 <= year <= 3000
    except ValueError:
        return False
# Function to check if the file extension is in the list of extensions
def check_extension(file_info,file_extensions):
    if file_info.name.lower().endswith(file_extensions):
        return True
    return False

# Function to get the available subfolder
# The most important is not to overwrite the files
# The number of files on the local directory is guranteed to be less than 500000
# The function returns the first available subfolder in the output directory
# The first subfolder shall start with 1 to keep the files in the folder even if the filename starts with a character which would cause stepping up to the target folder containing the numbered subfolders
# The function creates the subfolder if it doesn't exist
# The function returns None if it can't find an available subfolder after max_attempts
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
        logger.warning(f"Directory not found: {root_directory}", exc_info=True)
    except PermissionError as e:
        logger.warning(f"Permission denied: {root_directory}", exc_info=True)
    except Exception as e:
        logger.warning(f"Unexpected error in crawler: {e}", exc_info=True)

#Alternative solution for the crawler
#def crawl(root_directory, file_extensions = None):
#    logger = logging.getLogger()
#    try:
#        for path in root_directory.rglob('*'):
#            if path.is_file() and (file_extensions is None or path.suffix.lower() in file_extensions):
#                file_info = FileInfo(
#                    name = path.name,
#                    path = str(path),
#                    size = path.stat().st_size,
#                    mtime = datetime.datetime.fromtimestamp(path.stat().st_mtime)
#                )
#                yield file_info
#    except FileNotFoundError as e:
#        logger.error(f"Directory not found: {root_directory}", exc_info=True)
#    except PermissionError as e:
#        logger.error(f"Permission denied: {root_directory}", exc_info=True)
#    except Exception as e:
#        logger.error(f"Unexpected error in crawler: {e}", exc_info=True)

#Save database in a pickle file
def save_database_to_pickle(db, filepath):
    with open(filepath, 'wb') as f:
        pickle.dump(db, f)

#Load database from a pickle file
#If the file doesn't exist, return an empty dictionary which is handled later
def load_database_from_pickle(filepath):
    if os.path.exists(filepath):
        with open(filepath, 'rb') as f:
            db = pickle.load(f)
        return db
    else:
        print('hash map pickle doesnt exist')
        return {}
#Calculate hash files. The function is able to handle errors and return None in case of an error.
#The function is able to shorten the hash calculation to the first 100mb if the file size is greater than 1.5 Gb
#The function returns the hash value as a string
# Later the hash value is used as a key in the hash_map, and the size is checked to ensure further safety
def calc_hash(file_path, algo, chunk_size=65536, shorten=False):
    logger = logging.getLogger()
    """Compute the hash of a file."""
    if algo == "sha3":
        hash_algo=hashlib.sha3_256
        hash_obj = hash_algo()
    if algo == "blake2":
    #logger.debug("Hash algo: sha3-256")
        hash_obj = hashlib.blake2b(digest_size=64)
    try:
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(chunk_size)
                #Shorten option for optional use. Code is left here for future use.
                if shorten:
                    if f.tell() > 250 * 1024 * 1024:
                        logger.warning(f"Shortening (250mb) hash calculation for {file_path}")
                        break
                if not chunk:
                    break
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
    except Exception as e:
        logger.warning(f"Error hashing file {file_path}: {e}")
        return None

# Create a timestamped subfolder path
# The function returns a path with the current date and time
# The function is used to create a new subfolder in the output directory
def define_timestamped_subfolder_path(dir):
    now_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return Path(dir / now_str)

#Clean the hash map
#
def clean_hashmap(hash_map):
    """
    Returns a new hash_map containing only those entries whose file paths exist.
    Logs and omits entries for which the file path does not exist.
    """
    logger = logging.getLogger()
    cnt = Counter()
    # Build a new dictionary that only retains existing paths
    cleaned_hash_map = {}
    for file_hash, info in hash_map.items():
        cnt.update()
        if os.path.exists(info.path):
            cleaned_hash_map[file_hash] = info
        else:
            logger.debug(f"Removing missing file hash: {file_hash} (path not found: {info.path})")
    cnt.show()
    return cleaned_hash_map

if __name__ == "__main__":
    Collection = Path(r"")
    To_Check = Path(r"X:\TrashShit")
    output_main = Path(r"X:\Target")
    hashmappath = Path(r"X:\Target\SimpleStorage_blake2-512.pkl")
    #hashmappath = Path(r"X:\Target\SimpleStorage-sha3-256.pkl")
    algo = "blake2"
    #"sha3"
    #"blake2"
    hash_map = {}
    c = Counter()
    logger = global_logging(output_main)
    if Collection == Path() and not hashmappath:
        print("Missing input.")
        sys.exit()
    if not hashmappath == Path():
        hash_map = load_database_from_pickle(str(hashmappath))
    
    print(f"Collection: {Collection}")
    print(f"To_Check: {To_Check}")
    print(f"Output: {output_main}")
    print(f"Hash map: {hashmappath}")
    print(f"Algo: {algo}")
    ans = input(f"Do you want to continue with these conditions? (yes/no): ")
    if ans in ["yes", "y"]:
        pass
    else:
        print("Exiting...")
        sys.exit()
    
    logger.debug(f"Collection: {Collection}")
    logger.debug(f"To_Check: {To_Check}")
    logger.debug(f"Output: {output_main}")
    logger.debug(f"Hash map: {hashmappath}")
    logger.debug(f"Hash algo: {algo}")

    if not hash_map:
        for collection_files in crawler(str(Collection)):
            collection_files.hash = calc_hash(collection_files.path, algo)
            if collection_files.hash not in hash_map:
                hash_map[collection_files.hash] = collection_files
        save_database_to_pickle(hash_map,str(output_main / f"{Collection.name}.pkl"))

    for tobechecked in crawler(str(To_Check)):
        hashh = calc_hash(tobechecked.path, algo)
        if hashh is None:
            print(f"Error hashing file {tobechecked.path}")
            continue
        if hashh in hash_map:
            #print("Found")
            c.update()
            #target_dir = output_main / 'duplicates'
            #target_dir = get_available_subfolder(target_dir,tobechecked.name)
            #targetPathh = target_dir / tobechecked.name
            #try:
            #    shutil.move(tobechecked.path, targetPathh)
            #    print(f"File MOVED {tobechecked.path} to {targetPathh}")
            #except Exception as e:
            #    print(f'Move error {tobechecked} {e}')
        else:
            print("Not Found")
            print(tobechecked.path)
            logger.error(f"Missing file \n{tobechecked.path}")
    c.show()