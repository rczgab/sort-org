# Walk through file system
# hash
# compare functions
# database operations
import os
import hashlib
import sqlite3
import time
from datetime import datetime

# config variables
input_directory = r"/path/to/scan"


# walk through the file system starting from input_directory
def walk_file_system(input_directory):
    for root, dirs, files in os.walk(input_directory):
        for file in files:
            file_path = os.path.join(root, file)
            yield file_path

def collect_file_info(file_path):
    try:
        file_name = os.path.basename(file_path)
        extension = os.path.splitext(file_name)[1].lower()
        stats = os.stat(file_path)
        size = stats.st_size
        modified_time = datetime.fromtimestamp(stats.st_mtime).isoformat()
        return file_name, extension, size, modified_time
    except Exception as e:
        print(f"Error collecting info for {file_path}: {e}")
        return None, None

# Compute file hash
def compute_file_hash(file_path, hash_algo=hashlib.sha3_256,chunk_size=65536):
    hash_obj = hash_algo()
    try:
        with open(file_path, 'rb') as f:
            while chunk := f.read(chunk_size):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
    except Exception as e:
        print(f"Error hashing file {file_path}: {e}")
        return None



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



# Create database connection
def create_db_connection(db_path):
    conn = sqlite3.connect(db_path)
    return conn

#Create database table
def create_table(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY,
            path TEXT NOT NULL,
            hash TEXT,
            size INTEGER,
            modified_time TEXT
        )
    ''')
    conn.commit()

#        mime?
 #       encrypted?

 # Table columns: rowid, path, filename, extension, size, modified_time, hash1, hash2, mime_type, is_encrypted, last_checked, error, to_move,

 # Folder priority list

# open table, read entry, to_move?, move, if no error update last_checked. if error, log error, update error column.

#if file_path exists in db:, what if the sw is re-run?


#info mining functiondef get_file_info(file_path):