
import collections

import pipa
from pipa import Pipeline


def make_items_from_file(input):
    file_tuple = collections.namedtuple("FileTuple", "path, file_obj")
    item = file_tuple(path=input.name, file_obj=input)
    return item

session_pipe = Pipeline()
session_pipe.append( pipa.system.find_in_path )
session_pipe.append( pipa.system.open_files )
session_pipe.append( pipa.util.item.MakeItem, func=make_items_from_file )



