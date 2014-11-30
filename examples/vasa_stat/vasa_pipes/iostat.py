import collections
import arrow
import pipa

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
                    pipa.logger.error('unable to decode line: %s' % line)
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

iostat_pipe = pipa.Pipeline()
iostat_pipe.append( pipa.system.item.ReadFromFile, start_from_line=107814 )
iostat_pipe.append( pipa.util.item.Memory, fields_names=['line_num'] )
iostat_pipe.append( make_items_from_iostat )
