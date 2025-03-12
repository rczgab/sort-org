from counter_util import Counter
import os
import pickle
from pathlib import Path

#Clean the hash map
#
def clean_hashmap(hash_map):
    """
    Returns a new hash_map containing only those entries whose file paths exist.
    Logs and omits entries for which the file path does not exist.
    """
    cnt = Counter()
    # Build a new dictionary that only retains existing paths
    cleaned_hash_map = {}
    for file_hash, info in hash_map.items():
        cnt.update()
        if os.path.exists(info.path):
            cleaned_hash_map[file_hash] = info
        else:
            print(f"Removing missing file hash: {file_hash} (path not found: {info.path})")
    cnt.show()
    return cleaned_hash_map

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


if __name__ == "__main__":
    linkToHashMap = Path("")
    oldMap = load_database_from_pickle(linkToHashMap)

    newMap = clean_hashmap(oldMap)

    newMapPath = linkToHashMap.with_name(f"{linkToHashMap.stem}-clean{linkToHashMap.suffix}")
    save_database_to_pickle(newMap,newMapPath)

    print(f"saved to {newMapPath}")
