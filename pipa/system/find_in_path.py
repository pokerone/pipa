
import os
import fnmatch

import pipa

def find_in_path(iterable = [], root='',find=''):
    for path, dirlist, filelist in os.walk(root):
        for name in fnmatch.filter(filelist,find):
            yield os.path.join(path,name)