
import os 
import copy
import time




from influxdb import InfluxDBClient
influxdb_client = InfluxDBClient('10.6.70.130', 8086, "guest", "guest", "vasa_new")


import logging
logger=logging.getLogger('pipa')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - (%(funcName)20s.%(lineno)s) - %(levelname)s - %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)

import pipa
import pipe4


def modify_gc_timestamp(value, jvm_uptime=''):
    if value and jvm_uptime != '':
        new_value = copy.copy(jvm_uptime).replace(seconds=(float(value)))
        return new_value

def parse_files (session_dict, file_path, file_mask, write=True):
    #remap pipe
    remap_pipe = pipa.Pipeline()
    remap_pipe.append(pipa.util.item.Remap)
    #create_db pipe
    create_db_item_pipe = pipa.Pipeline()
    create_db_item_pipe.append( pipe4.create_db_item )


    #--------execution
    for tuple in pipe4.session_pipe.execute(root=file_path, find=file_mask):
        print tuple.path
        if tuple.path.endswith("gc"):
            pipe4.gc_pipe.configure_item('make_item', func_kwargs={'hostname':session_dict['host']})
            for gc_tuple in pipe4.gc_pipe.execute(tuple):
                for new_gc_tuple in remap_pipe.execute( gc_tuple, field_name='timestamp', func=modify_gc_timestamp, func_kwargs={'jvm_uptime':session_dict['jvm_uptime']}):
                    for gc_tuple_db in create_db_item_pipe.execute(new_gc_tuple, session_dict=session_dict):
                        if write:
                            influxdb_client.write_points( gc_tuple_db )
                        logger.info("line n.%s inserted as %s" % (pipe4.gc_pipe.pipe_memory('line_num'), gc_tuple_db) )
        elif tuple.path.endswith("gcutil"):
            for gcutil_tuple in pipe4.gcutil_pipe.execute( tuple ):
                for new_gcutil_tuple in remap_pipe.execute( gcutil_tuple, field_name='timestamp', func=modify_gc_timestamp, func_kwargs={'jvm_uptime':session_dict['jvm_uptime']}):
                    for new_gcutil_tuple_db in create_db_item_pipe.execute( new_gcutil_tuple, session_dict=session_dict):
                        if write:
                            influxdb_client.write_points( new_gcutil_tuple_db )
                        logger.info("line n.%s inserted as %s" % (pipe4.gcutil_pipe.pipe_memory('line_num'), new_gcutil_tuple_db) )
        elif tuple.path.endswith("iostat"):
            for iostat_tuple in pipe4.iostat_pipe.execute(tuple):
                for new_iostat_tuple_db in create_db_item_pipe.execute(iostat_tuple, session_dict=session_dict):
                    if write:
                        influxdb_client.write_points( new_iostat_tuple_db )
                    logger.info("line n. %s inserted as %s" % (pipe4.iostat_pipe.pipe_memory('line_num'), new_iostat_tuple_db) )
        elif tuple.path.endswith("prstat"):
            for prstat_tuple in pipe4.prstat_pipe.execute(tuple):
                for new_prstat_tuple_db in create_db_item_pipe.execute(prstat_tuple, session_dict=session_dict):
                    if write:
                        influxdb_client.write_points( new_prstat_tuple_db )
                    logger.info("line n. %s inserted as %s" % (pipe4.prstat_pipe.pipe_memory('line_num'), new_prstat_tuple_db) )
        elif tuple.path.endswith("prstat_thread"):
            for prstat_thread_tuple in pipe4.prstat_thread_pipe.execute(tuple):
                for new_prstat_thread_tuple_db in create_db_item_pipe.execute( prstat_thread_tuple, session_dict=session_dict):
                    if write:
                        influxdb_client.write_points( new_prstat_thread_tuple_db )
                        logger.info("line n. %s inserted as %s" % (pipe4.prstat_thread_pipe.pipe_memory('line_num'), new_prstat_thread_tuple_db) )
        elif tuple.path.endswith("dspool"):
            pipe4.dspool_pipe.configure_item('make_ts_dspool', start_time=session_dict['start_monitoring_time'], step_sec=6)
            for dspool_tuple in pipe4.dspool_pipe.execute(tuple, field_name='file_obj'):
                for new_dspool_tuple_db in create_db_item_pipe.execute( dspool_tuple, session_dict=session_dict ):
                    if write:
                        influxdb_client.write_points( new_dspool_tuple_db )
                    print new_dspool_tuple_db
                    #logger.info("line n. %s inserted as %s" % (pipe4.dspool_pipe.pipeline_memory['line_num'], new_dspool_tuple_db) )

def main():

    file_list=  ["/home/andrea/tmp/log/196/9ZZaaZa*",
                "/home/andrea/tmp/log/196/az909-Z*",
                "/home/andrea/tmp/log/195/0AZ9zA0*",
                "/home/andrea/tmp/log/195/az00zAa*"]

    file_list=  ["C:\\temp\\vasa_check\\log\\196\\9ZZaaZa*",
                "C:\\temp\\vasa_check\\log\\196\\az909-Z*",
                "C:\\temp\\vasa_check\\log\\195\\0AZ9zA0*",
                "C:\\temp\\vasa_check\\log\\195\\az00zAa*"]

    file_list=  ["C:\\temp\\vasa_check\\log\\196\\az909-Z*"]

    #file_list=  ["C:\\temp\\vasa_check\\log\\196\\az909-Z*","C:\\temp\\vasa_check\\log\\195\\0AZ9zA0*"]

    session_dict={}
    for f in file_list:
        root=os.path.dirname(f)
        filemask=os.path.basename(f)
        #retrieve session
        for key, value in pipe4.session_parser_pipe.execute(root=root, find=filemask+".log"):
            session_dict[key] = value
        for line in pipe4.jvm_uptime_pipe.execute(root=root, find=filemask+"_jvm_uptime"):
            session_dict[line[0]] = line[1]
        session_dict['host']='oss'+ os.path.basename(root)
        print session_dict
        parse_files(session_dict, root, filemask+'*gc*', write=True)

if __name__ == '__main__':
    main()
