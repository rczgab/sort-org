# Description: This script is designed to find duplicate files based on their content and metadata.
# The script is capable of handling a large number of files and can be run multiple times on the same dataset.
# The script is run as a single instance. It is not designed to be run in parallel.
# The script is designed to be run on both Windows or Mac operating system.
# The script is designed to be run on a local filesystem.
# shutil.move is guaranteed to be atomic, a rename operation on the same drive and on the same filesystem.

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

# --- Constants and configuration ---

#Config
#Root folder containing possible duplicates
#root_directory = r"X:\2_Storage\2_DUPLICATES\ROOT\partial"
root_directory = r"X:\2_Storage\2_DUPLICATES\4th"
#Folder to move the unique files to
#output_main = r"X:\2_Storage\2_DUPLICATES\2ndStorage"
output_main = r"X:\2_Storage\2_DUPLICATES\2ndStr"
#Optional link to previously stored hash map


hashMaintainBit = False

#link_hash_map = 'X:/Target/T_hashmap.pkl'
link_hash_map = ''



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
#Return the corresponding string for the naming of the subfolder, based on the filetype.
def type_selector(file_info):
    if check_extension(file_info,image_Exif_ext):
        return 'img'
    elif check_extension(file_info, image_ext):
        return 'img'
    elif check_extension(file_info, video_ext):
        return 'video'
    elif check_extension(file_info, subscript_ext):
        return 'subscript'
    elif check_extension(file_info, audio_ext):
        return 'audio'
    elif check_extension(file_info, pdf_ext):
        return 'pdf'
    elif check_extension(file_info, compressed_ext):
        return 'compressed'
    elif check_extension(file_info, doc_ext):
        return 'doc'
    elif check_extension(file_info, image_mac):
        return 'heic'
    else:
        return 'other'

##Alternative for development purposes
#extension_map = {
#    image_Exif_ext: 'img',
#    image_ext: 'img',
#    video_ext: 'video',
#    ...
#}
#
#def type_selector(file_info) -> str:
#    for ext_tuple, label in extension_map.items():
#        if file_info.name.lower().endswith(ext_tuple):
#            return label
#    return 'other'

    
# --- Helper functions ---
#Counter funtion class
class Counter:
    def __init__(self):
        self.cr = 0
        self.mr = 0

    def update(self):
        if self.cr > 999:
            self.mr += self.cr
            print(f"Feldolgozott fájlok száma: {self.mr}")
            #The current file should already count, so the counter starts at 1
            self.cr = 1
        else:
            self.cr += 1

    def clear(self):
        self.cr = 0
        self.mr = 0

    def show(self):
        print(f"Elemszám: {self.mr + self.cr}")
    
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

#Path checkers
#Check if the folder exists, if not, quit the program
#Only used to check the main (input, output) folders as the first step, where quitting is appropriate
def folder_dont_exist_quit(folder_path):
    if not os.path.exists(folder_path):
        print(f"{os.path.basename(folder_path)} dir not existing!")
        sys.exit()
#Formatting input path to be able to input Windows or Unix path as is
def input_path_formatting(folder_path):
    dir = folder_path.replace('\\','/')
    return os.path.normpath(dir)
# Main folder check, returns the formatted path
def main_folder_check(folder_path):
    dir = input_path_formatting(folder_path)
    print(dir)
    folder_dont_exist_quit(dir)
    return dir

#File handler helpers
#Joining paths and normalizing them to be able to use path in Windows or Unix
def join_norm_path(*paths):
    return os.path.normpath(os.path.join(*paths))
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
def get_available_subfolder(output_dir, base_name, max_attempts = 500000):
    logger = logging.getLogger()

    subfolder_index = 1
    
    while subfolder_index < max_attempts:
        subfolder_path = os.path.normpath(os.path.join(output_dir, str(subfolder_index)))
        if not os.path.exists(subfolder_path):
            os.makedirs(subfolder_path)
        if not os.path.exists(os.path.normpath(os.path.join(subfolder_path, base_name))):
            return subfolder_path
        subfolder_index += 1
    
    logger.warning(f"Could not find available subfolder after {max_attempts} attempts.", exc_info=True)
    
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

#Unique classes
#Image processor class used to extract exif data from images
class ImageProc:
    def __init__(self):
        pass

    def get_exif_creation_date(self, filepath):

        logger = logging.getLogger()

        def parse_exif_date(date_string):
            for fmt in date_formats:
                try:
                    return datetime.datetime.strptime(date_string, fmt)
                except ValueError:
                    continue
            return None
        
        try:
            with open(filepath, 'rb') as image_file:
                try:
                    tags = exifread.process_file(image_file, details=False, debug=True)
                except Exception as e:
                    logger.debug(f"Error extracting Exif data from {filepath}: {e}", exc_info=True)
                date_tag = (
                    tags.get("EXIF DateTimeOriginal")
                )
                if date_tag:
                    date_string = str(date_tag)
                    dt = parse_exif_date(date_string)
                    if dt:
                        return dt
                    else:
                        logger.debug(f"Unrecognized date format in {filepath}: {date_string}")
        except Exception as e:
            logger.debug(f"Error extracting Exif data from {filepath}: {e}", exc_info=True)
        return None
    

def post_process_hash(hash_map):
    #Defined later
    pass

# Create a timestamped subfolder path
# The function returns a path with the current date and time
# The function is used to create a new subfolder in the output directory
def define_timestamped_subfolder_path(dir):
    now_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return join_norm_path(dir, now_str)

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

#Calculate the distance between the mtime and exif time
#The function is used to decide which file is the best version of the file
#The function returns the distance in seconds
# The exif time should signify the exposure time of the image.# If both images have an exif time, the one with modification time closer to the exif time is considered better.
#If one of the files has no exif time, the one with the exif time is considered better.
#If both files have no exif time, the one with the older modification time is considered better.
# If a modification time is before the exif time, the file is considered corrupted which results it being worse in every case.
# If the modification time is before the exif time, the distance is increased by a large offset to ensure that the file is always considered worse, as the modification time shall not be older then the time of the exposure.
# If the modification time is before the exif time - which is the time of the exposure - the file's date is most likely corrupted. Which is not preferable, so there is a large offset to ensure that the file is always considered worse.
#If both image has modification time before the exif time, the one with the smaller distance is considered better.
# Modification time shall always be available.
# Exif time is optional.
def exif_distance(mtime: datetime.datetime, exif_time: datetime.datetime) -> float:
    if mtime + datetime.timedelta(hours=2, seconds=1) < exif_time:
        # add a large offset so that times before exif_time 
        # are always considered worse if there's a time after exif_time
        offset = 10**12
        return offset + abs((exif_time - mtime).total_seconds())
    else:
        # normal difference in seconds
        return abs((mtime - exif_time).total_seconds())


if __name__ == '__main__':
    ### Setup
    #The counter should be used to count the number of files processed by sections. It shall be reset after each section.

    #Checks for input path integrity
    root_directory = main_folder_check(root_directory)
    output_main = main_folder_check(output_main)

    now_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    #Start utilities
    global_logging(output_main)

    logging.getLogger("exifread").setLevel(logging.WARNING)
    
    count = Counter()
    image_processor = ImageProc()

    logger = logging.getLogger()

    path_map = {}
    hash_map = {}

    print(f"""
    Root: {root_directory}
    Output main: {output_main}
    Link to hashmap: {link_hash_map}
    Hashmaintain? {hashMaintainBit}
    """)
    ans = input("Do you want to continue using these parameters? (yes/no): ")
    if ans in ["yes", "y"]:
        print("Continuing")
    else:
        print("Exiting the program.")
        sys.exit()
    
    
    if link_hash_map:
        hash_map = load_database_from_pickle(link_hash_map)
        #Cleanup for development purposes
        print('Cleanup started')
        hash_map = clean_hashmap(hash_map)
        print('Cleanup finished')

    #Process 1, build info of new files

    #Crawl through input folder
    #Iterate and fill out basic file information for the path_map
    print(f"Crawl started: {root_directory}")
    for file_info in crawler(root_directory):
        count.update()
        path_map[file_info.path] = file_info
    count.show()
    print('Crawl ended.')

    #Process 2, build hash map and decide the best version of the files
    #
    print('Hash map build started.')
    #Clear
    count.clear()
    #For showing the currently processed folder
    dict_t = ''
    #Collecting irregularities
    odd_files = []

    #Collect alternatives
    alternative_files = []

    #Iterate through the path_map
    for path, info in path_map.items():
        #Logging the progress print the current directory
        dict_new = os.path.dirname(path)
        if dict_new != dict_t:
            print(f'{dict_new}')
        #Calculate hash
        #Alternative
        # Calc hash only from the first 100mb if the file size is greater than 1.5 Gb
        #if check_extension(info,video_ext) and info.size > 1.5 * 1024 * 1024 * 1024:
        #    info.hash = calc_hash(info.path, shorten=True)
        #else:
        info.hash = calc_hash(info.path)
        #Check if the hash calculation failed
        if info.hash is None:
            #Log the error
            logger.error(f"Hash calculation failed for {info.path}")
            #Add the invalid file to the invalid list
            odd_files.append(info.path)
            #Skip the rest of the loop
            continue
        #Check if the file is an image with possible exif data
        #Clear the exif time
        info.exif_time = None
        if check_extension(info,image_Exif_ext):
                #get image creation date
                #If two files share the same full-file hash, we assume they share the same EXIF info, but for safety, the exif info is always extracted and stored for every file.
                creation_date = image_processor.get_exif_creation_date(info.path)
                info.exif_time = creation_date

        #Check if the hash is already in the hash_map
        if info.hash in hash_map:
            new_mtime_entry = info.mtime
            old_mtime_entry = hash_map[info.hash].mtime
            #Due to hash value changing with different metadata, the same hash value must contain the same exif date. If not, the file is considered irregular.
            exif_time = hash_map[info.hash].exif_time
            new_exif_time = info.exif_time
            #If the size is different, the file is considered irregular. Might be caused by the shortening of the hash calculation. Stored as irregularity to be checked later manually.
            if info.size != hash_map[info.hash].size:
                logger.error(f"Size mismatch at {info} and {hash_map[info.hash]} where {info.hash}: {info.size} != {hash_map[info.hash].size}")
                #Add the invalid file to the invalid list
                odd_files.append(info.path)
                continue

            if exif_time != new_exif_time:
                #The oddity of the exif time mismatch is logged as they should be the same for the same hash value.
                logger.error(f"Exif time mismatch at {info} and {hash_map[info.hash]} where {info.hash}: {new_exif_time} != {exif_time}")
                #Add the invalid file to the invalid list
                odd_files.append(info.path)
                continue
            #Compare
            if exif_time:
                #If exif time from the hashmap is available, check if new exif time is available
                if new_exif_time:
                    #If both exif times are available, compare using distance logic
                    try:
                        dist_old = exif_distance(old_mtime_entry, exif_time)
                        dist_new = exif_distance(new_mtime_entry, exif_time)
                        if dist_new < dist_old:
                            if hashMaintainBit:
                                alternative_files.append(info.path)
                            else:
                                hash_map[info.hash] = info
                            #development purposes
                            #logger.warning(f"FileHash EXIF updated! Old: {hash_map[info.hash]} New: {info}")
                            #print('update')
                            print(f"Better alternative found new mod time NEW:: {info} is closer to exif than the old one: OLD:: {hash_map[info.hash]}\nNEW mod time: {info.mtime} exif: {info.exif_time}\nOLD mod time: {hash_map[info.hash].mtime} exif: {hash_map[info.hash].exif_time}\nNEW::{dist_new} OLD::{dist_old} ")
                    except Exception as e:
                        logger.error(f"Exif time comparison failed at {info} and {hash_map[info.hash]}")
                        #Add the invalid file to the invalid list
                        odd_files.append(info.path)
                        continue
                    #development purposes
                        #if new_mtime_entry < old_mtime_entry:
                        #    hash_map[info.hash] = info
                else:
                    #if exif time from the hashmap is available, but new exif time is not available, choose the hashmap version
                    #Do nothing, leave the file in the root folder
                    pass
            else:
                #If hashmap exif time is not available, check for new exif time availability
                if new_exif_time:
                    #if hashmap exif is not available, but new exif time is available for the same hash, choose the new exif time version
                    if hashMaintainBit:
                        alternative_files.append(info.path)
                    else:
                        hash_map[info.hash] = info
                    print(f"Better image alternative found, new exif {info} exist, old not: {hash_map[info.hash]}")
                else:
                    #if hashmap exif is not available and new exif is also not available, compare modification times, where the older modification time is considered the best version
                    if new_mtime_entry < old_mtime_entry:
                        #if the new from pathmap is older than the one already stored in hashmap, update. Else, keep the one already in the hashmap.
                        if hashMaintainBit:
                            alternative_files.append(info.path)
                        else:
                            hash_map[info.hash] = info
                        
                        print(f"Better alternative found no new exif: NEW:: {info}, no old exif OLD:: {hash_map[info.hash]} ")
                        #logger.warning(f"FileHash NORMAL updated! Old: {hash_map[info.hash]} New: {info}")
                        #print('update')
        #If the hash is not in the hash_map, add it
        else:
            #Add the new file to the hash_map
            if hashMaintainBit:
                alternative_files.append(info.path)
            else:
                hash_map[info.hash] = info
            #development purposes
            #logger.warning(f"File added to hashmap as new entry: {info}")
            #print('new')
            #print(f"New file found: {info}")
            count.update()
        dict_t = os.path.dirname(path)
    #development purposes
    #print("Virtually added files to hashmap:")
    count.show()
    print('Hash map build ended.')

#if None:
    #if hash_map:
    if not hashMaintainBit:
        movement_info = []
        print('Hash map processing started.')
        count.clear()
        #Process 3 - Move files to target directory
        #Iterate through the hash_map
        #Move the files to the target directory with subfolders by year and type, and numbered subfolders to avoid name conflicts
        #Move the unique files only which were chosen as best versions. Leave the duplicates in their original place.
        for hash, info in hash_map.items():
            year = info.mtime.year
            #Select type
            type_str = type_selector(info)
            if type_str == 'img':
                if info.exif_time:
                    type_str = join_norm_path(type_str, 'exif')
                    if info.exif_time.year:
                        year = info.exif_time.year
                else:
                    type_str = join_norm_path(type_str, 'no_exif')

            if is_year(year):
                target_dir = join_norm_path(output_main, now_str, type_str, str(year))
            else:
                target_dir = join_norm_path(output_main, now_str, type_str)

            target_dir = get_available_subfolder(target_dir,info.name)
            if not target_dir:
                logger.error(f"No subfolder available")
                odd_files.append(info.path)
                continue
            target_path = join_norm_path(target_dir,info.name)

            if not os.path.exists(target_path):
                if os.path.exists(info.path):
                    try:
                        shutil.move(info.path, target_path)
                        movement_info.append(f"File MOVED {info.path} to {target_path}")
                        #logger.info(f"File MOVED {info.path} to {target_path}")
                        #Check if the move was really successful and only update the path if the file is really moved.
                        #if os.path.exists(target_path):
                        #    checkback_size = os.path.getsize(target_path)
                        #    checkback_name = os.path.basename(target_path)
                        #    checkback_mtime = datetime.datetime.fromtimestamp(os.path.getmtime(target_path))
                        #    checkback_exif_time = None
                        #    if check_extension(info,image_Exif_ext):
                        #        #get image creation date
                        #        checkback_exif_time = image_processor.get_exif_creation_date(target_path)
                        #    if checkback_size == info.size and checkback_name == info.name and checkback_mtime == info.mtime and checkback_exif_time == info.exif_time:
                        #        #Update the hash map with the new path
                        #        #update hash's info.path to the new path which after the move shall be the correct path
                        #        hash_map[hash].path = target_path
                        #    else:
                        #        logger.error(f"Shouldn't reach here, something went wrong with relocation, re-checked info DO NOT MATCH {info.path} {target_path}")
                        #
                        #else:
                        #    logger.error(f"Shouldn't reach here, something went wrong with relocation {info.path} {target_path}")
                        count.update()
                    except Exception as e:
                        logger.error(f"Moving error {info} {target_path} {e}", exc_info=True)
                else:
                    logger.error(f"Shouldn't reach here, not existing original path something went wrong with relocation {info} {target_path}", exc_info=True)
            else:
                logger.error(f"Shouldn't reach here, something went wrong with relocation {info} {target_path}", exc_info=True)
        print('Hash map process ended.')
        #At this point, the hash map exist with: every hash has only one entry, which is the oldest, or if available the closest to the exif based creation date, meaning they are the best versions. The rest of the files are left in their original place. The hash map's path are updated to the path after the move.
        pickle_hash_map_path = join_norm_path(output_main, os.path.basename(root_directory) + '_hashmap.pkl')
        #Save the hash map to a pickle file to be able to load the already hashed unique database later.
        save_database_to_pickle(hash_map, pickle_hash_map_path)
        logger.info(f"Hashmap pickle path: {pickle_hash_map_path}")
        print('Hash map saved to pickle.')
        #Save movement info as pickle.
        pickle_movementinfopath = join_norm_path(output_main, os.path.basename(root_directory) + '_movement.pkl')
        save_database_to_pickle(movement_info, pickle_movementinfopath)
        logger.info(f"Movement pickle path: {pickle_movementinfopath}")
        print('Movement info saved to pickle.')
        count.show()

#The irregular files are moved to a separate folder to be checked manually later.
    if odd_files:
        target_dir = join_norm_path(output_main, now_str, 'odd_files')
        for path in odd_files:
            dir = get_available_subfolder(target_dir, os.path.basename(path))
            target_path = join_norm_path(dir, os.path.basename(path))
            if not target_path:
                logger.error(f"No subfolder available at odd files!!")
                print(path)
                continue
            if not os.path.exists(target_path):
                try:
                    shutil.move(path, target_path)
                    logger.info(f"Odd file MOVED {path} to {target_path}")
                except Exception as e:
                    logger.error(f"Moving odd file error {path} {target_path} {e}", exc_info=True)
    else:
        print('No odd files found.')
#The alternative files are moved to a separate folder to be checked manually later.
    if alternative_files:
        target_dir = join_norm_path(output_main, now_str, 'alternative_files')
        for path in alternative_files:
            if os.path.exists(path):
                dir = get_available_subfolder(target_dir, os.path.basename(path))
                target_path = join_norm_path(dir, os.path.basename(path))
                if not target_path:
                    logger.error(f"No subfolder available at alternative files!!")
                    print(path)
                    continue
                if not os.path.exists(target_path):
                    try:
                        shutil.move(path, target_path)
                        logger.info(f"Alternative file MOVED {path} to {target_path}")
                    except Exception as e:
                        logger.error(f"Moving alternative file error {path} {target_path} {e}", exc_info=True)
            else:
                logger.info(f"Alternative file path not exists! {path}")
    else:
        print('No alternative files found.')
    print('End of program.')



    

