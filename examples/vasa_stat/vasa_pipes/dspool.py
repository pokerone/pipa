import arrow
import collections
import pipa


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


