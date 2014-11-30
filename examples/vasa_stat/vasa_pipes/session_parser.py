
import arrow
import pipa

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

session_parser_pipe = pipa.Pipeline()
session_parser_pipe.append( pipa.system.find_in_path )
session_parser_pipe.append( pipa.system.open_files )
session_parser_pipe.append( pipa.system.read_from_files )
session_parser_pipe.append( make_key_value_from_session )

