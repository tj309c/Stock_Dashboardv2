import os

def list_files(path):
    files = os.listdir(path)
    print(f"Found {len(files)} files.")
    for filename in files:
        print(filename)

list_files(".")