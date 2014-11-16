
import collections

import pipa
from pipa import Pipeline, PipelineItem

def check_useful_lines(lines):
    for line in lines:
        first_char = line[0]
        if first_char != ''  and ( first_char == '#' or first_char > 0 ):
                yield line

def make_tuple(lines):
    for line in lines:
        if line != '' and len(line) > 1:
            if line.startswith('#'):
                method_name = line.split("#")[1].strip(' \t\n\r')
                Method = collections.namedtuple("Method", 'type name')
                yield Method(type='method', name=method_name)
            else:
                try:
                    error_code = line.split("\t",1)[0].strip(' \t\n\r')
                    message = line.split("\t",1)[1].rsplit("\t",1)[0].strip(' \t\n\r')
                    from_service = line.rsplit("\t",1)[1].strip(' \t\n\r')
                    Error = collections.namedtuple("Error", 'type code message from_service')
                    yield Error(type='error', code=error_code, message=message, from_service=from_service)
                except IndexError as e:
                    Ignore = collections.namedtuple("Ignore", 'type')
                    print "Unable to decode: %s" % line
                    print e
                    yield(Ignore(type='ignore'))

def create_csv(tuples, output_file=''):
    with open(output_file, 'w') as file:
        method_name = 'undefined'
        for item in tuples:
            if item.type == 'method':
                method_name = item.name
            elif item.type == 'error':
                file.write(";".join([method_name, item.code, item.message, item.from_service, '\n']))

p = Pipeline()
p.add_item( pipa.system.find_in_path, _item_name='find_files')
p.add_item( pipa.system.open_files )
p.add_item( pipa.system.read_from_files  )
p.add_item( check_useful_lines )
p.add_item( make_tuple )
#p.add_item( PipelineItem(create_csv, item_name='create_csv', output_file='c:\\temp\\result.csv') )

#tuple_list = [item for item in p.execute(root=r'c:\\temp\\lavoro\\jpig_monitor\\',find='error_code.txt')]

p1=Pipeline()
p1.add_item( pipa.system.find_in_path, _item_name='find_files')
p1.add_item( pipa.system.open_files )
p1.add_item( pipa.system.item.ReadFromFile )
p1.add_item( pipa.util.item.PrintInput )
#p1.execute(root=r'c:\\temp\\lavoro\\jpig_monitor\\',find='error_code.txt')

p2=Pipeline()
p2.add_item(pipa.system.remote.ParamikoSSHConnection)
p2.add_item( pipa.util.item.PrintInput )
p2.execute(['osx098v.vizzavi.it'])

