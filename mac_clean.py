import os
from collections import namedtuple
import datetime
import logger
import logging
import shutil
from counter_util import Counter
from mutagen.mp3 import MP3
from pathlib import Path
import fnmatch

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

def condition_movies(file_info):
    movies_ext = ('.mp4', '.avi', '.mov', '.mpeg','.mkv','.mts', '.mpg', '.flv', '.3gp', '.wmv')
    if file_info.name.lower().endswith(movies_ext):
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
    
def condition_shortmp3(file_info):
    if file_info.name.lower().endswith('.mp3'):
        try:
            audio = MP3(file_info.path)
            duration = audio.info.length
            return duration < 5
        except Exception as e:
            print("Error processing mp3 path")
            return False
    return False

def condition_Thumbs(file_info):
    if file_info.name == 'Thumbs.db':
        return True
    return False

def condition_filename(file_info, pattern):
    if fnmatch.fnmatch(file_info.name, pattern):
        return True
    return False

def condition_organize(file_info):
    """return condition = True and output subdir, based on the extension and the modification date.
    e.g. song.mp3 -> type selector -> audio -> mp3 -> 2021 -> song.mp3"""
    try:
        output_dir = Path(output_main)
        label = type_selector(file_info)
        year = file_info.mtime.year
        path = Path(file_info.path)
        extension = path.suffix.lower()
        subdir = output_dir / label / extension[1:] / str(year)
        return True, str(subdir)
    except Exception as e:
        logger.error(f"Error in organize: {e}", exc_info=True)
        return False, None

root_dir = Path(r"X:\_SAFE\0_DATA_SAFE\Movies")
output_main = Path(r"X:\AppleShit")

if __name__ == '__main__':
    count = Counter()

    
    #output_dir = "X:/FIXVERSION/other_simple"
    
    logger.global_logging(output_main)
    logger = logging.getLogger(__name__)

    other_ext = ('.nfo',)
    #('.sift','.php','.peft','.xsl', '.xsd','.xspf','.xst','.track','.thumb','.pp','.pcam','.a','.air','.dll','.exe')
    #('.pp','.diz','.fpc','ocx','.dll','.pas','.bak','.c','.h','.cpp')
    #('.gp3','.gp4')
    #('.iso','.las','.7z','.zip','.rar')
    subscript_ext = ('.srt', '.ass')

    for file_i in crawler(str(root_dir)):
        count.update()
        output_dir = output_main
        
        #condition = True
        #condition = condition_extension(file_i, other_ext)
        #condition = condition_moveAppleFiles(file_i)
        #condition = condition_movies(file_i, movies_ext)
        #condition = condition_shortmp3(file_i)
        #condition = condition_Thumbs(file_i)
        #condition, output_dir = condition_organize(file_i)
        condition = condition_filename(file_i,'RARBG.txt')

        if condition:
            #print(file_i.name)
            move(output_dir, file_i)
    count.show()

