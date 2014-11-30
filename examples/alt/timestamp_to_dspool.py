
import os
import collections

import arrow


import logging
logger=logging.getLogger('pipa')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - (%(funcName)20s.%(lineno)s) - %(levelname)s - %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)

import pipa
import pipe4

def make_ts_dspool(inputs, start_time='', step_sec=6):
    st = arrow.get(start_time)
    for input in inputs:
        #line = input.line.split()
        line = input.split()
        st = st.replace(seconds=+step_sec)
        line[0] = st.format('YYYY-MM-DDTHH:mm:ss')
        line = " ".join(line)
        yield (line)

def make_items_from_dspool(input_list):
    DSPoolTuple= collections.namedtuple("DSPoolTuple", "timestamp,trans_ActiveCount,vasa_AverageCreationTime,vasa_TotalCreationTime,trans_AverageBlockingTime,trans_MaxWaitTime,vasa_ActiveCount,trans_TimedOut,vasa_AvailableCount,vasa_TotalBlockingTime,vasa_CreatedCount,trans_AverageCreationTime,trans_DestroyedCount,trans_AvailableCount,trans_CreatedCount,vasa_MaxUsedCount,vasa_DestroyedCount,trans_MaxCreationTime,vasa_TimedOut,vasa_MaxWaitTime,trans_TotalCreationTime,vasa_AverageBlockingTime,vasa_MaxCreationTime,trans_MaxUsedCount,trans_TotalBlockingTime")
    for input in input_list:
        line = input
        print line
        trans_data = {}
        vasa_data = {}
        timestamp_string = line.split('"',1)[0].strip(" \t\r\n")
        timestamp = arrow.get(timestamp_string, format("YYYY-MM-DDTHH:mm:ss"))

        splitted_line = line.split('{')
        points = {}
        points['timestamp'] = splitted_line[0].strip(" \r\t\n")
        for value in splitted_line[2].strip(" \r\t\n").replace('"', "").replace(' => ', '=').replace("}", "").strip().split(","):
            k, v = value.split("=")
            points['trans_' + k.strip()] = int(v)
        for value in splitted_line[4].strip(" \r\t\n").replace('"', "").replace(' => ', '=').replace("}", "").strip().split(","):
            k, v = value.split("=")
            points['vasa_' + k.strip()] = int(v)

        yield DSPoolTuple(**points)

def make_items_from_file(input):
    file_tuple = collections.namedtuple("FileTuple", "path, file_obj")
    item = file_tuple(path=input.name, file_obj=input)
    return item

dspool_pipe = pipa.Pipeline()
dspool_pipe.append( pipa.system.find_in_path )
dspool_pipe.append( pipa.system.open_files )
dspool_pipe.append( pipa.util.item.MakeItem, func=make_items_from_file )
dspool_pipe.append( pipa.processing.filters.Select, field_name='file_obj')
dspool_pipe.append( pipa.system.read_from_files )
dspool_pipe.append( make_ts_dspool )
dspool_pipe.append( make_items_from_dspool)

"""
dspool_pipe.add_item( pipa.util.item.Memory, fields_names=['line_num'] )

"""
session_dict={}
file_list=  ["C:\\temp\\vasa_check\\log\\196\\az909-Z*"]
for f in file_list:
    root=os.path.dirname(f)
    filemask=os.path.basename(f)

    #retrieve session
    for key, value in pipe4.session_parser_pipe.execute(root=root, find=filemask+".log"):
        session_dict[key] = value
    session_dict['host']='oss'+ os.path.basename( root )

    dspool_pipe.configure_item('make_ts_dspool', start_time=session_dict['start_monitoring_time'], step_sec=6)

    for line in dspool_pipe.execute(session_dict, root, filemask+'dspool*'):
        print line



