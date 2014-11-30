
import arrow
import pipa

#--------jvm uptime
def parse_jvm_uptime(lines):
    for line in lines:
        ts_string = line.split("/")[0].strip(" \t\r\n")
        uptime_ts = int(line.split("/")[1].split(">")[1].strip(" \t\r\n")[:-1])
        key = 'jvm_uptime'
        value = arrow.get(ts_string, "YYYY-MM-DDTHH:mm:ss").replace(seconds=(int(uptime_ts/1000)* -1) )
        yield key, value

jvm_uptime_pipe = pipa.Pipeline()
jvm_uptime_pipe.append( pipa.system.find_in_path )
jvm_uptime_pipe.append( pipa.system.open_files )
jvm_uptime_pipe.append( pipa.system.read_from_files )
jvm_uptime_pipe.append( parse_jvm_uptime )


