
import copy
import json
import collections

import arrow
import logbook
logger=logbook.Logger("pipa"+__name__)

import pipa
from pipa import Pipeline


def make_items_from_file(input):
    file_tuple = collections.namedtuple("FileTuple", "path, file_obj")
    item = file_tuple(path=input.name, file_obj=input)
    return item

#--------session
session_pipe = Pipeline()
session_pipe.append( pipa.system.find_in_path )
session_pipe.append( pipa.system.open_files )
session_pipe.append( pipa.util.item.MakeItem, func=make_items_from_file )

#--------gcutil
def make_items_from_gcutil(inputlist):
    for input in inputlist:
        gc_util_tuple= collections.namedtuple("GCUtilTuple", "timestamp,S0,S1,E,O,P,YGC,YGCT,FGC,FGCT,GCT")
        input = input.line.strip(' \t\n\r')
        try:
            if input[0].isdigit():
                fields = input.split()
                item = gc_util_tuple(timestamp=fields[0],
                                     S0=float(fields[1]),
                                     S1=float(fields[2]),
                                     E=float(fields[3]),
                                     O=float(fields[4]),
                                     P=float(fields[5]),
                                     YGC=int(fields[6]),
                                     YGCT=float(fields[7]),
                                     FGC=int(fields[8]),
                                     FGCT=float(fields[9]),
                                     GCT=float(fields[10]))
                yield item
        except ValueError as e:
            logger.error(e)
            logger.error(input)

gcutil_pipe = Pipeline()
gcutil_pipe.append( pipa.system.item.ReadFromFile )
gcutil_pipe.append( pipa.util.item.Memory, fields_names=['line_num'] )
gcutil_pipe.append( make_items_from_gcutil )

#--------gc
def make_items_from_gc(input, hostname=''):
    gc_tuple= collections.namedtuple("GCTuple", "timestamp,S0C,S1C,S0U,S1U,EC,EU,OC,OU,PC,PU,YGC,YGCT,FGC,FGCT,GCT,hostname")
    try:
        input = input.line.strip(' \t\n\r')
        if input[0] != 'T' and int(input[0]) < 10:
            fields = input.split()
            item = gc_tuple(timestamp=fields[0],
                                 S0C=int(fields[1].split(".")[0])*1024,
                                 S1C=int(fields[2].split(".")[0])*1024,
                                 S0U=int(fields[3].split(".")[0])*1024,
                                 S1U=int(fields[4].split(".")[0])*1024,
                                 EC=int(fields[5].split(".")[0])*1024,
                                 EU=int(fields[6].split(".")[0])*1024,
                                 OC=int(fields[7].split(".")[0])*1024,
                                 OU=int(fields[8].split(".")[0])*1024,
                                 PC=int(fields[9].split(".")[0])*1024,
                                 PU=int(fields[10].split(".")[0])*1024,
                                 YGC=int(fields[11]),
                                 YGCT=int(fields[12].split(".")[0]),
                                 FGC=int(fields[13]),
                                 FGCT=int(fields[14].split(".")[0]),
                                 GCT=int(fields[15].split(".")[0]),
                                 hostname=hostname)
            return item
    except ValueError as e:
        logger.error( e )
        logger.error( input )


gc_pipe = Pipeline()
gc_pipe.append( pipa.system.item.ReadFromFile )
gc_pipe.append( pipa.util.item.Memory, fields_names=['line_num'] )
gc_pipe.append( pipa.util.item.MakeItem, func=make_items_from_gc )


#--------iostat
import arrow

def make_items_from_iostat(input_list):
    iostat_tuple= collections.namedtuple("IOStatTuple", "timestamp, sd0_rps, sd0_wps, sd0_util, sd1_rps, sd1_wps, sd1_util, sd2_rps, sd2_wps, sd2_util, sd3_rps, sd3_wps, sd3_util")
    current_data_timestamp = None
    for input in input_list:
        line = input.line.strip(' \t\n\r')
        if len(line.split()) == 5:
            #it's a timestamp
            try:
                current_data_timestamp  = arrow.get(line,'ddd MMM DD HH:mm:ss YYYY')
            except arrow.ParserError:
                try:
                    current_data_timestamp  = arrow.get(line,'ddd MMM  D HH:mm:ss YYYY')
                except arrow.ParserError:
                    logger.error('unable to decode line: %s' % line)
        if len(line.split()) == 12 and not line.startswith('rps'):
            #it's data
            data = {}
            for x in range(0,4):
                disk_name = "".join(['sd', str(x)])
                rps, wps, util = line.split()[3*x:(3*x)+3]
                data["_".join([disk_name, 'rps'])] = int(rps)
                data["_".join([disk_name, 'wps'])] = int(wps)
                data["_".join([disk_name, 'util'])] = float(util)
            data['timestamp'] = current_data_timestamp
            current_data_timestamp = ''
            yield iostat_tuple(**data)

iostat_pipe = Pipeline()
iostat_pipe.append( pipa.system.item.ReadFromFile, start_from_line=107814 )
iostat_pipe.append( pipa.util.item.Memory, fields_names=['line_num'] )
iostat_pipe.append( make_items_from_iostat )


#--------prstat
import arrow

def make_items_from_prstat(input_list):
    PRStatTuple= collections.namedtuple("PRStatTuple", "timestamp, pid, username, usr, sys, trp, tfl, dfl, lck, slp, lat, vcx, icx, scl, sig")
    for input in input_list:
        try:
            line = input.line.strip(' \t\n\r')
            timestamp_string= " ".join(line.split()[0:4])
            timestamp_string= " ".join([timestamp_string, line.split()[5]])
            current_data_timestamp = ''
            try:
                current_data_timestamp  = arrow.get(timestamp_string,'ddd MMM DD HH:mm:ss YYYY')
            except :
                try:
                    current_data_timestamp  = arrow.get(timestamp_string,'ddd MMM D HH:mm:ss YYYY')
                except:
                    logger.error('unable to decode timestamp: %s' % timestamp_string)
            line_array = line.split()[6:]
            yield PRStatTuple( timestamp = current_data_timestamp ,
                                pid = int(line_array[0]),
                                username = line_array[1],
                                usr = float(line_array[2]),
                                sys = float(line_array[3]),
                                trp = float(line_array[4]),
                                tfl = float(line_array[5]),
                                dfl = float(line_array[6]),
                                lck = float(line_array[7]),
                                slp = float(line_array[8]),
                                lat = float(line_array[9]),
                                vcx = float(line_array[10]),
                                icx = float(line_array[11]),
                                scl = float(line_array[12]),
                                sig = float(line_array[13]))
        except ValueError:
            pass
        except IndexError as e:
            print "Exeception: ", e
prstat_pipe = Pipeline()
prstat_pipe.append( pipa.system.item.ReadFromFile)
prstat_pipe.append( pipa.util.item.Memory, fields_names=['line_num'] )
prstat_pipe.append( make_items_from_prstat )

#--------prstat_thread
def make_items_from_prstat_thread(input_list):
    PRStatThreadTuple= collections.namedtuple("PRStatThreadTuple", "timestamp, pid, username, usr, sys, trp, tfl, dfl, lck, slp, lat, vcx, icx, scl, sig")
    for input in input_list:
        line = input.line.strip(' \t\n\r')
        timestamp_string= " ".join(line.split()[0:4])
        timestamp_string= " ".join([timestamp_string, line.split()[5]])

        line_array = line.split()[6:]
        try:
            line = input.line.strip(' \t\n\r')
            timestamp_string= " ".join(line.split()[0:4])
            timestamp_string= " ".join([timestamp_string, line.split()[5]])
            current_data_timestamp = ''
            try:
                current_data_timestamp  = arrow.get(timestamp_string,'ddd MMM DD HH:mm:ss YYYY')
            except:
                try:
                    current_data_timestamp  = arrow.get(timestamp_string,'ddd MMM D HH:mm:ss YYYY')
                except:
                    logger.error('unable to decode line: %s' % timestamp_string)

            line_array = line.split()[6:]
            yield PRStatThreadTuple( timestamp = current_data_timestamp,
                                pid = int(line_array[0]),
                                username = line_array[1],
                                usr = float(line_array[2]),
                                sys = float(line_array[3]),
                                trp = float(line_array[4]),
                                tfl = float(line_array[5]),
                                dfl = float(line_array[6]),
                                lck = float(line_array[7]),
                                slp = float(line_array[8]),
                                lat = float(line_array[9]),
                                vcx = float(line_array[10]),
                                icx = float(line_array[11]),
                                scl = float(line_array[12]),
                                sig = float(line_array[13]))
        except ValueError:
            pass
        except IndexError as e:
            print e

prstat_thread_pipe = Pipeline()
prstat_thread_pipe.append( pipa.system.item.ReadFromFile)
prstat_thread_pipe.append( pipa.util.item.Memory, fields_names=['line_num'] )
prstat_thread_pipe.append( make_items_from_prstat_thread )

def print_arg(*args, **kwargs):
    print kwargs

#--------dspool

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
        points = {}
        splitted_line = line.split('{')
        points['timestamp'] = arrow.get(splitted_line[0].strip(" \r\t\n"), format("YYYY-MM-DDTHH:mm:ss"))
        try:
            for value in splitted_line[2].strip(" \r\t\n").replace('"', "").replace(' => ', '=').replace("}", "").strip().split(","):
                k, v = value.split("=")
                points['trans_' + k.strip()] = int(v)
            for value in splitted_line[4].strip(" \r\t\n").replace('"', "").replace(' => ', '=').replace("}", "").strip().split(","):
                k, v = value.split("=")
                points['vasa_' + k.strip()] = int(v)
            yield DSPoolTuple(**points)
        except IndexError as e:
            pipa.logger.error("Error parsing line %s" % line)
            pipa.logger.error("Exception was: %s", e)



dspool_pipe = pipa.Pipeline()
dspool_pipe.append( pipa.processing.filters.Select, field_name='file_obj')
dspool_pipe.append( pipa.system.read_from_files )
dspool_pipe.append( make_ts_dspool )
dspool_pipe.append( make_items_from_dspool)

#--------session parser
def make_key_value_from_session(lines):
    for line in lines:
        try:
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
        except:
            pipa.logger.error("Error parsing line: '%s'. Ignoring" % line.strip(" \t\r\n"))

session_parser_pipe = Pipeline()
session_parser_pipe.append( pipa.system.find_in_path )
session_parser_pipe.append( pipa.system.open_files )
session_parser_pipe.append( pipa.system.read_from_files )
session_parser_pipe.append( make_key_value_from_session )

#--------jvm uptime
def parse_jvm_uptime(lines):
    for line in lines:
        ts_string = line.split("/")[0].strip(" \t\r\n")
        uptime_ts = int(line.split("/")[1].split(">")[1].strip(" \t\r\n")[:-1])
        key = 'jvm_uptime'
        value = arrow.get(ts_string, "YYYY-MM-DDTHH:mm:ss").replace(seconds=(int(uptime_ts/1000)* -1) )
        yield key, value

jvm_uptime_pipe = Pipeline()
jvm_uptime_pipe.append( pipa.system.find_in_path )
jvm_uptime_pipe.append( pipa.system.open_files )
jvm_uptime_pipe.append( pipa.system.read_from_files )
jvm_uptime_pipe.append( parse_jvm_uptime )

#--------create_db_item
def create_db_item(input_list, session_dict):
    db_item = collections.namedtuple("DbItem", "json_data")
    for input in input_list:
        if input != None:
            data = {}
            if not getattr(input, 'hostname', None) == None:
                data['name'] = input.hostname + '.' + type(input).__name__
            else:
                data['name'] = type(input).__name__
            data['points'] = []
            data['columns'] = []
            temp_data = {}
            points = []
            for field_name in input._fields:
                temp_data[field_name] = getattr(input, field_name)
            for field_name, field_value in temp_data.iteritems():
                if field_name == 'timestamp':
                    field_name = 'time'
                if type(field_value).__name__ == 'Arrow':
                    field_value = float(field_value.timestamp)
                if field_name == 'time':
                    try:
                        field_value = float(field_value)
                    except:
                        print field_value

                data['columns'].append(field_name)
                if type(field_value) == type([]):
                    for value in field_value:
                        points.append(value)
                else:
                    points.append(field_value)

            #modify or add some general field
            for field_name in "item_creation_timestamp,host,session_id".split(","):
                if field_name == 'item_creation_timestamp':
                    data['columns'].append(field_name)
                    points.append(arrow.now().timestamp)
                if field_name == 'host':
                    data['columns'].append(field_name)
                    points.append(session_dict['host'])
                if field_name == 'session_id':
                    data['columns'].append(field_name)
                    points.append("_".join([session_dict['session_name'], str(session_dict['start_monitoring_time'].timestamp)]))
            data['points'] = [points]
            import pprint
            #pprint.pprint(json.dumps([data]))
            #item = db_item(json_data=json.dumps([data]))
            yield json.dumps([data])
