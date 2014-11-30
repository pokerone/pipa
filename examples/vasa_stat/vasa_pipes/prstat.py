
import arrow
import collections

import pipa

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
                    pipa.logger.error('unable to decode timestamp: %s' % timestamp_string)
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
prstat_pipe = pipa.Pipeline()
prstat_pipe.append( pipa.system.item.ReadFromFile)
prstat_pipe.append( pipa.util.item.Memory, fields_names=['line_num'] )
prstat_pipe.append( make_items_from_prstat )


