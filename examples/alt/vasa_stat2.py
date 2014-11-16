
import copy
import time

import pipa
import pipe

from logbook import Logger
logger_name='parse_files'
logger = Logger(logger_name)
from influxdb import InfluxDBClient
influxdb_client = InfluxDBClient('10.6.70.130', 8086, "guest", "guest", "vasa_stat")

def modify_gc_timestamp(value, jvm_uptime=''):
    if value and jvm_uptime != '':
        new_value = copy.copy(jvm_uptime).replace(seconds=(float(value)))
        return new_value

def parse_files (session_dict, file_path, file_mask):
    #remap pipe
    remap_pipe = pipa.Pipeline()
    remap_pipe.add_item(pipa.util.item.Remap)
    #create_db pipe
    create_db_item_pipe = pipa.Pipeline()
    create_db_item_pipe.add_item( pipe.create_db_item )

    #--------execution
    for tuple in pipe.session_pipe.execute(root=file_path, find=file_mask):
        print tuple.path
        if tuple.path.endswith("gc"):
            for gc_tuple in pipe.gc_pipe.execute(tuple):
                for new_gc_tuple in remap_pipe.execute( gc_tuple, field_name='timestamp', func=modify_gc_timestamp, func_kwargs={'jvm_uptime':session_dict['jvm_uptime']}):
                    for gc_tuple_db in create_db_item_pipe.execute(new_gc_tuple, session_dict=session_dict):
                        time.sleep(0.1)
                        influxdb_client.write_points( gc_tuple_db )
                        logger.info("line n.%s inserted as %s" % (pipe.gc_pipe.pipeline_memory['line_num'], gc_tuple_db) )
        elif tuple.path.endswith("gcutil"):
            for gcutil_tuple in pipe.gcutil_pipe.execute( tuple ):
                for new_gcutil_tuple in remap_pipe.execute( gcutil_tuple, field_name='timestamp', func=modify_gc_timestamp, func_kwargs={'jvm_uptime':session_dict['jvm_uptime']}):
                    for new_gcutil_tuple_db in create_db_item_pipe.execute( new_gcutil_tuple, session_dict=session_dict):
                        time.sleep(0.1)
                        influxdb_client.write_points( new_gcutil_tuple_db )
                        logger.info("line n.%s inserted as %s" % (pipe.gcutil_pipe.pipeline_memory['line_num'], new_gcutil_tuple_db) )
        elif tuple.path.endswith("iostat"):
            for iostat_tuple in pipe.iostat_pipe.execute(tuple):
                for new_iostat_tuple_db in create_db_item_pipe.execute(iostat_tuple, session_dict=session_dict):
                    time.sleep(0.1)
                    influxdb_client.write_points( new_iostat_tuple_db )
                    logger.info("line n. %s inserted as %s" % (pipe.iostat_pipe.pipeline_memory['line_num'], new_iostat_tuple_db) )
        elif tuple.path.endswith("prstat"):
            for prstat_tuple in pipe.prstat_pipe.execute(tuple):
                for new_prstat_tuple_db in create_db_item_pipe.execute(prstat_tuple, session_dict=session_dict):
                    time.sleep(0.1)
                    influxdb_client.write_points( new_prstat_tuple_db )
                    logger.info("line n. %s inserted as %s" % (pipe.prstat_pipe.pipeline_memory['line_num'], new_prstat_tuple_db) )
        elif tuple.path.endswith("prstat_thread"):
            for prstat_thread_tuple in pipe.prstat_thread_pipe.execute(tuple):
                for new_prstat_thread_tuple_db in create_db_item_pipe.execute( prstat_thread_tuple, session_dict=session_dict):
                    time.sleep(0.1)
                    influxdb_client.write_points( new_prstat_thread_tuple_db )
                    logger.info("line n. %s inserted as %s" % (pipe.prstat_thread_pipe.pipeline_memory['line_num'], new_prstat_thread_tuple_db) )

        elif tuple.path.endswith("dspool"):
            for dspool_tuple in pipe.dspool_pipe.execute(tuple):
                for new_dspool_tuple_db in create_db_item_pipe.execute( dspool_tuple, session_dict=session_dict ):
                    influxdb_client.write_points( new_dspool_tuple_db )
                    logger.info("line n. %s inserted as %s" % (pipe.dspool_pipe.pipeline_memory['line_num'], new_dspool_tuple_db) )


def main():
    """
    session_dict={}
    for key, value in pipe.session_parser_pipe.execute(root='C:\\temp\\vasa_check\\log\\195', find='0AZ9zA0*log'):
        session_dict[key] = value
    for key, value in pipe.jvm_uptime_pipe.execute(root='C:\\temp\\vasa_check\\log\\195', find='0AZ9zA0_jvm_uptime'):
        session_dict[key] = value
    session_dict['host']='oss195'
    session_dict['session_name']='0AZ9zA0'
    print session_dict
    parse_files(session_dict, 'C:\\temp\\vasa_check\\log\\195', '0AZ9zA0*' )
    """
    session_dict={}
    for key, value in pipe.session_parser_pipe.execute(root='C:\\temp\\vasa_check\\log\\196', find='9aZAz9Z*log'):
        session_dict[key] = value
    for key, value in pipe.jvm_uptime_pipe.execute(root='C:\\temp\\vasa_check\\log\\196', find='9aZAz9Z_jvm_uptime'):
        session_dict[key] = value
    session_dict['host']='oss196'
    session_dict['session_name']='9aZAz9Z'
    parse_files(session_dict, 'C:\\temp\\vasa_check\\log\\196', '9aZAz9Z*dspool*' )

if __name__ == '__main__':
    main()
