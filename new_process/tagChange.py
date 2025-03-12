
#pip install eyeD3

import subprocess
import glob
from pathlib import Path

# Set the starting directory
start_dir = Path(r"/Users/gabor/Music/Musix_safe")

# Recursively find all mp3 files
mp3_files = list(start_dir.rglob('*.mp3'))

# Print found files
for mp3_file in mp3_files:
    try:
        subprocess.run(["eyeD3", "--to-v2.3", mp3_file])
        print(mp3_file)
    except Exception as e:
        print(f"Error processing {mp3_file}: {e}")
        continue
print("Done")
