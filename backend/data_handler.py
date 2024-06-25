import json
import shutil
import os

JSON_FILE = 'something.json'
DESTINATION_PATH = '../frontend/something.json'
# DESTINATION_PATH = '/var/www/abouabid/emploi/something.json'

def load_existing_data():
    try:
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"{JSON_FILE} not found. Starting with an empty list.")
        return {'data': [], 'last_updated': None}
    except json.JSONDecodeError:
        print(f"Error decoding JSON from {JSON_FILE}. Starting with an empty list.")
        return {'data': [], 'last_updated': None}

def save_data(data):
    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    # Ensure the destination directory exists
    os.makedirs(os.path.dirname(DESTINATION_PATH), exist_ok=True)
    shutil.copy(JSON_FILE, DESTINATION_PATH)
    print(f"Data has been saved to {JSON_FILE} and copied to {DESTINATION_PATH}")

def reassign_ids(data):
    for i, row in enumerate(data):
        row['id'] = i + 1
    return data

def check_ids(data):
    ids = [row['id'] for row in data]
    missing_ids = [i for i in range(1, max(ids) + 1) if i not in ids]
    duplicate_ids = set([id for id in ids if ids.count(id) > 1])
    if missing_ids:
        print(f"Missing IDs: {missing_ids}")
    if duplicate_ids:
        print(f"Duplicate IDs: {duplicate_ids}")
