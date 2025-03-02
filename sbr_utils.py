import os

def separate_path_extension(file_path):
    # Get the directory and the filename
    directory, filename = os.path.split(file_path)
    
    # Separate the filename and the extension
    name, extension = os.path.splitext(filename)
    
    return directory, name, extension
