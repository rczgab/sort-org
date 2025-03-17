import os
from collections import namedtuple
import datetime
import logger
import logging
import shutil
from counter_util import Counter
from mutagen.mp3 import MP3

#

def crawler(root_directory):
    # Define the namedtuple
    FileInfo = namedtuple('FileInfo', ['name', 'path', 'size', 'mtime'])
    try:
        with os.scandir(root_directory) as entries:
            for entry in entries:
                if entry.is_dir(follow_symlinks=False):
                    yield from crawler(entry.path)
                elif entry.is_file(follow_symlinks=False):
                    # Access file information using DirEntry
                    file_info = FileInfo(
                        name = entry.name,
                        path = entry.path,
                        size = entry.stat().st_size,
                        mtime = datetime.datetime.fromtimestamp(entry.stat().st_mtime),
                        #'ctime': datetime.datetime.fromtimestamp(entry.stat().st_ctime),
                    )
                    yield file_info
    except FileNotFoundError as e:
        logger.error(f"Directory not found: {root_directory}", exc_info=True)
    except PermissionError as e:
        logger.error(f"Permission denied: {root_directory}", exc_info=True)
    except Exception as e:
        logger.error(f"Unexpected error in crawler: {e}", exc_info=True)

def get_available_subfolder(output_dir, base_name, max_attempts = 500000):
    subfolder_index = 1
    while subfolder_index < max_attempts:
        subfolder_path = os.path.normpath(os.path.join(output_dir, str(subfolder_index)))
        if not os.path.exists(subfolder_path):
            os.makedirs(subfolder_path)
        if not os.path.exists(os.path.normpath(os.path.join(subfolder_path, base_name))):
            return subfolder_path
        subfolder_index += 1
    logger.error(f"Could not find available subfolder after {max_attempts} attempts.", exc_info=True)
    return None

def condition_moveAppleFiles(file_info):
    if file_info.name.startswith('._'):
        if file_info.size == 4 * 1024:
            return True
    elif file_info.name == '.DS_Store':
        return True
    return False

def condition_extension(file_info,file_extensions):
    if file_info.name.lower().endswith(file_extensions):
        return True
    return False

def condition_movies(file_info, file_extensions):
    if file_info.name.lower().endswith(file_extensions):
        if file_info.size > 1 * 1024 * 1024 *1024:
            return True
    return False

def move(output_dir, file_i):
    subdir_path = get_available_subfolder(output_dir,file_i.name)
    new_path = os.path.normpath(os.path.join(subdir_path,file_i.name))
    if not os.path.exists(new_path):
        try:
            shutil.move(file_i.path,new_path)
            logger.info(f"File {file_i.path} moved to {new_path}")
            #print(new_path)
        except Exception as e:
            logger.error(f"Error during moving {file_i.path} to {new_path}")

def is_shortmp3(file_path):
    try:
        audio = MP3(file_path)
        duration = audio.info.length
        return duration < 5
    except Exception as e:
        print("Error processing mp3 path")
        return False

if __name__ == '__main__':
    count = Counter()

    root_dir = "X:/testrun/audio-test"
    
    #output_dir = "X:/FIXVERSION/other_simple"
    output_dir = "X:/testrun/test_trash"
    
    logger.global_logging(output_dir)
    logger = logging.getLogger(__name__)

    mp3_ext = ('.mp3',)
    #('.sift','.php','.peft','.xsl', '.xsd','.xspf','.xst','.track','.thumb','.pp','.pcam','.a','.air','.dll','.exe')
    #('.pp','.diz','.fpc','ocx','.dll','.pas','.bak','.c','.h','.cpp')
    #('.gp3','.gp4')
    #('.iso','.las','.7z','.zip','.rar')
    subscript_ext = ('.srt', '.ass')
    movies_ext = ('.mp4', '.avi', '.mov', '.mpeg','.mkv','.mts', '.mpg', '.flv', '.3gp', '.wmv')

    for file_i in crawler(root_dir):
        count.update()
        """
        If it starts with a point -- File
        if it doesn't have a point -- File
        """
        #extension_dir = os.path.splitext(file_i.name)[1][1:]
        #target_dir = os.path.normpath(os.path.join(output_dir, extension_dir))

        #condition = True
        #condition = condition_moveAppleFiles(file_i)

        condition = False
        if (condition_extension(file_i, mp3_ext)):
            if (is_shortmp3(file_i)):
                condition = True

        
        
        #condition = condition_extension(file_i, other_ext)
        #if not condition:
        #    if file_i.name == 'Thumbs.db':
        #        condition = True


        #condition = condition_movies(file_i, movies_ext)

        if condition:
            move(output_dir, file_i)
    count.show()

