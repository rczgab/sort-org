
#pip install eyeD3
import subprocess
import glob
from pathlib import Path

from mutagen.mp3 import MP3
from mutagen.id3 import ID3, ID3NoHeaderError

# Global dictionary to track ID3 versions
versions = {}



def check_id3_version(file_path):
    try:
        audio = MP3(file_path, ID3=ID3)
    except ID3NoHeaderError:
        print(f"{file_path}: No ID3 tag found")
        versions["No ID3"] = versions.get("No ID3", 0) + 1
        return
    
    if audio.tags is None:
        print(f"{file_path}: No ID3 tag found")
        versions["No ID3"] = versions.get("No ID3", 0) + 1
        return

    # Check if it's an ID3v2 tag
    if isinstance(audio.tags, ID3):
        ver = f"ID3v2.{audio.tags.version[0]}.{audio.tags.version[1]}"
        versions[ver] = versions.get(ver, 0) + 1
        print(f"{file_path}: {ver}")

    # Check for ID3v1 tags (stored as a simple dictionary in mutagen)
    elif "TIT2" not in audio.tags:
        versions["ID3v1"] = versions.get("ID3v1", 0) + 1
        print(f"{file_path}: ID3v1")


# Set the starting directory
start_dir = Path(r"/Users/gabor/Music/Musix_safe")

# Recursively find all mp3 files
mp3_files = list(start_dir.rglob('*.mp3'))

print(versions)
# Print found files
for mp3_file in mp3_files:
    check_id3_version(mp3_file)
print(versions)

for mp3_file in mp3_files:
    try:
        audio = MP3(mp3_file, ID3=ID3)
        audio.save(v2_version=4)
    except Exception as e:
        print(f"Error processing {mp3_file}: {e}")
        continue
print("Done")