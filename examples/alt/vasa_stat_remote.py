import collections
import pipa
import pipe

import arrow

from logbook import Logger
logger_name='parse_files'
logger = Logger(logger_name)

from influxdb import InfluxDBClient
influxdb_client = InfluxDBClient('10.6.70.130', 8086, "guest", "guest", "vasa_stat")



#--------------------------------------------------------------------------------------open remote files
def make_item_for_paramiko(item):
    new_item = collections.namedtuple("ParamikoInput", "host, user, pwd, key_path, path")
    user =''
    pwd = ''
    key_path=''
    if "@" in item.netloc:
        user=item.netloc.split("@")[0]
        address=item.netloc.split("@")[1]
        if ":" in user:
            pwd=user.split(":")[1]
            user=user.split(":")[0]
        if ":" in address:
            address = address[:-1]
    else:
        address = item.netloc
    return new_item(host=address, user=user, pwd=pwd, key_path=key_path, path=item.path)

remote_pipe = pipa.Pipeline()
remote_pipe.add_item( pipa.util.item.ParseUrl )
remote_pipe.add_item( pipa.util.item.Memory, fields_names=['netloc','path'] )
remote_pipe.add_item( pipa.util.item.MakeItem, func=make_item_for_paramiko )
remote_pipe.add_item( pipa.system.remote.ParamikoSSHConnection )

#--------------------------------------------------------------------------------------parse session file
def make_key_value_from_session(lines):
    for line in lines:
        line = line.line
        key = False
        value = False
        temp_line = line.split("]")[1].strip(" \t\r\n")
        temp_key = temp_line.split(":")[1].strip(" \t\r\n")
        temp_value = temp_line.split(":",2)[2].strip(" \t\r\n")

        if 'pid' in  temp_key and "jboss" in temp_key:
            key = "jboss_pid"
            value = temp_value
        if temp_key == "Starting monitoring time":
            key = "start_monitoring_time"
            value = arrow.get(temp_value, "YYYY-MM-DDTHH:mm:ss")
        if temp_key == 'Session name':
            key='session_name'
            value= temp_value
        if temp_key == 'GMT Time':
            key='start_time_gmt'
            tz = temp_value[len(temp_value)-3:]
            value = arrow.get(temp_value[:-4],"YY-MM-DDTHH:mm:ss")
        if temp_key == 'TZ Time':
            key='start_time_tz'
            tz = temp_value[len(temp_value)-3:]
            value = arrow.get(temp_value[:-4],"YY-MM-DDTHH:mm:ss")
        if key and value:
            yield key, value

read_pipe=pipa.Pipeline()
read_pipe.add_item(pipa.system.remote.ReadFromFile)
read_pipe.add_item( make_key_value_from_session )

#--------------------------------------------------------------------------------------parse remote log file
parse_files_pipe = pipa.Pipeline()
parse_files_pipe.add_item(pipa.system.remote.FindInPath)
parse_files_pipe.add_item(pipa.system.remote.OpenFiles)

pipe.gc_pipe.add_item( pipa.processing.filters.GreaterThen, field_name='timestamp', value=0)


def main():
    session_files = ["ssh://alaspada:PincoPallo090@oss196.vizzavi.it:/app/jboss/tmp/az909-Z.log"]
    for file in session_files:
        session_dict = {}
        for conn in remote_pipe.execute(file):
            #parse session file
            for k,v in read_pipe.execute(conn, path=remote_pipe.pipeline_memory['path']):
                session_dict[k] = v
            print session_dict

            #parse log files
            for file in parse_files_pipe.execute(conn, path="/app/jboss/tmp/", filemask=session_dict['session_name'] + "_*"):
                if file.path.endswith("_gc"):
                    print file
                    for line in pipe.gc_pipe.execute(file):
                        print line

if __name__ == '__main__':
    main()
