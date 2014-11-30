
import pipa
import collections

def make_items_from_file(input):
    file_tuple = collections.namedtuple("FileTuple", "path, file_obj")
    item = file_tuple(path=input.name, file_obj=input)
    return item

pipe = pipa.Pipeline()
pipe.append( pipa.system.find_in_path )
pipe.append( pipa.system.open_files )
pipe.append( pipa.util.item.MakeItem, func=make_items_from_file )

pipe1 = pipa.Pipeline()
pipe1.append( pipa.system.item.ReadFromFile )
pipe1.append( pipa.util.item.Memory, fields_names=['line_num'] )

for file in pipe.execute(root='c:\\temp\\vasa_check', find='*.log'):
    for line in pipe1.execute(file):
        print pipe1.pipe_memory('line_num')
