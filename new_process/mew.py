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
import regex

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


def remove_duplicate_words_ignore_case(input_string):
    words = input_string.split()
    encountered = set()
    result = []

    for w in words:
        # Check case-insensitively
        if w.lower() not in encountered:
            result.append(w)
            encountered.add(w.lower())

    return " ".join(result)

def get_audio_hash(file_path):
    logger = logging.getLogger()
    try:
        audio = AudioSegment.from_file(file_path)
        data = audio.raw_data
        return hashlib.sha3_256(data).hexdigest()
    except Exception as e:
        logger.error(f"Error processing {file_path}: {e}")
        return None
    
@dataclass
class AudioInfo:
    name: str
    path: str
    mtime: datetime.datetime
    hash: str = field(default="")
    metadata: Optional[dict[str, list[str]]] = field(default=None)

forbidden_words = {'unknown', 'ismeretlen', 'előadó', 'artist', 'album'}

def count_forbidden_words(input_str):
    count = 0
    for word in input_str.split():
        if word.lower() in forbidden_words:
            count += 1
    return count

if __name__ == '__main__':
    
    root_dir = Path(r"X:\testrun\audio-test\1980")
    output_dir = Path(r"X:\testrun\test_out")

    logger = global_logging(output_dir)

    hashmap = {}

    for mp3_file_path in root_dir.rglob("*.mp3"):
        print(f"Processing {mp3_file_path}")
        audio_hash = get_audio_hash(mp3_file_path)
        if audio_hash is None:
            logger.error(f"Error hashcalc none {mp3_file_path}")
            continue
        audio_file = AudioInfo(name=mp3_file_path.name, path=mp3_file_path, mtime=datetime.datetime.fromtimestamp(mp3_file_path.stat().st_mtime), hash=audio_hash)
        try:
            metadata = EasyID3(mp3_file_path)
        except Exception as e:
            metadata = EasyID3()

        if audio_file.hash not in hashmap:
            audio_file.metadata = metadata
            hashmap[audio_file.hash] = audio_file
            print(f"Added.")
        else:
            existing_entry = hashmap[audio_file.hash]
            existing_metadata = existing_entry.metadata
            print(f"Existing metadata \n{existing_metadata}")

            for key, new_val_list in metadata.items():
                if key not in existing_metadata:
                    existing_metadata[key] = new_val_list
                else:
                    # unify the existing list with the new list
                    combined = set(existing_metadata[key]) | set(new_val_list)
                    # If you want a list, convert the set back
                    existing_metadata[key] = list(combined)
            print(f"New metadata \n{existing_metadata}")

            if audio_file.mtime < existing_entry.mtime:
                existing_entry.path = audio_file.path
                existing_entry.mtime = audio_file.mtime
                print(f"Switched mdate old: {existing_entry.mtime} - new: {audio_file.mtime}")
            if count_forbidden_words(audio_file.name) < count_forbidden_words(existing_entry.name):
                existing_entry.name = audio_file.name
                print(f"old name: {existing_entry.name} new name: {audio_file.name}")
    
    for hash, mp3 in hashmap.items():
        try:
            subprocess.run(["eyeD3", "--to-v2.3", mp3.path], check=True)
            print(f"{mp3.path} eye3D processed.")
        except Exception as e:
            logger.error(f"Error processing {mp3.path}: {e}")
            continue
        
        pattern = r"[^\p{L}\p{N}\s_]"
        print(f"{mp3.metadata}")
        for key, value_list in mp3.metadata.items():
            if isinstance(value_list, list):
                new_list = []
                seen = set()
                for text in value_list:
                    cleaned = regex.sub(pattern, "", text, flags=regex.UNICODE)
                    new_text = cleaned.strip()
                    lowertext = new_text.lower()
                    cleared_words = []
                    for word in lowertext.split():
                        if word not in forbidden_words:
                            cleared_words.append(word)
                    lowertext = " ".join(cleared_words)
                    if lowertext not in seen:
                        seen.add(new_text.lower())
                        new_list.append(new_text)
                mp3.metadata[key] = new_list

            #TODO:: delete before publishing
            #mp3.metadata[key] = remove_duplicate_words_ignore_case(mp3.metadata[key])

            if mp3.metadata[key] == '':
                mp3.metadata[key] = 'Unknown'
            elif mp3.metadata[key] == ['']:
                mp3.metadata[key] = ['Unknown']
            
            #TODO: Check if needed
            #if len(mp3.metadata[key]) > 255:
            #    logger.warning(f"Truncating metadata for {mp3.name} - {key}. {mp3.metadata[key]}")
            #    mp3.metadata[key] = mp3.metadata[key][:255]
        print(f"{mp3.metadata}")
        try:
            hash_audio = EasyID3(mp3.path)
            hash_audio.update(mp3.metadata)
            hash_audio.save()
            logger.info(f"Metadata saved for {mp3.name}")
        except Exception as e:
            logger.error(f"Error saving metadata for {mp3.path}: {e}")
            continue
        
        try:
            subfolder = output_dir / mp3.path.relative_to(root_dir).parent
            best_name = "_".join(mp3.name.split())
            target_path= output_dir / subfolder / best_name
            logger.info(f"{mp3.path}\nfrom:to\n{mp3.name}\n{best_name}")



            if target_path.exists():
                subfold = get_available_subfolder(target_path.parent, best_name)
                target_path = subfold / best_name
                logger.warning(f"File {mp3.name} already exists, moving to {subfold}")

            if target_path.exists():
                logger.error(f"File {mp3.name} already exists in {subfold}, skipping")
                continue

            target_path.parent.mkdir(parents=True, exist_ok=True)

            shutil.move(mp3.path, target_path)
            
            logger.info(f"Moved {mp3.name} to {target_path}")
        except Exception as e:
            logger.error(f"Error moving {mp3.name} to {target_path}: {e}")
            continue
                
        

