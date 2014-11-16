
import pipa

def read_from_files(files_list, start_from_tell=0, **kwargs):
    for file in files_list:
        file.seek(start_from_tell)
        for line in file:
            yield line