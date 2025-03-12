import subprocess
from pathlib import Path

root_dir = Path(r"X:\testrun\audio-test")
c=0
for mp3_file_path in root_dir.rglob("*.mp3"):
    c=c+1
    if c%1000==0:
        print(c)
    try:
        subprocess.run(["eyeD3", "--to-v2.4", mp3_file_path])
    except subprocess.CalledProcessError as e:
        print(f"Error processing {mp3_file_path}: {e.stderr}")
        continue



    


