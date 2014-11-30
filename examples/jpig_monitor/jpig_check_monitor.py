
import sys
import logging
from collections import defaultdict

logger=logging.getLogger('pipa')
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - (%(funcName)20s.%(lineno)s) - %(levelname)s - %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)

import pipa
import jpig_pipes

from jpig_pipes.cm_pipe import cm_pipe
from jpig_pipes.create_conn import create_conn

def autovivify(levels=1, final=dict):
    return (defaultdict(final) if levels < 2 else defaultdict(lambda: autovivify(levels - 1, final)))

user='alaspada'
password=":" + 'PincoPallo090'

subsystem = ['cm','ma','ug']
hosts = ['oss179s','oss180s','oss181s']

subsystem = ['ma']
hosts=['oss179s']
conn_string='ssh://{user}{passwd}@{hostname}.vizzavi.it/app/jpig/jboss/server/PIG/log/jpig-{ss}-monitor.log'

counters=autovivify(4,list)

for ss in subsystem:
    for host in hosts:
        final_conn_string=conn_string.format(hostname=host, ss=ss, user=user, passwd=password)
        for conn_tuple in create_conn.execute(final_conn_string):
            if ss=='cm':
                cm_pipe.configure_item('grep', value='Frontend')
                cm_pipe.configure_item('parse_line', result_dict=counters)
                for parsed_file in cm_pipe.execute(conn_tuple, create_conn.pipe_memory('path')):
                    sys.stdout.write("line no: " + str(cm_pipe.pipe_memory('line_num')) + "\r")
                sys.stdout.write("\n")
            elif ss=='ma':
                cm_pipe.configure_item('grep', value='Backend')
                cm_pipe.configure_item('parse_line', result_dict=counters)
                for parsed_file in cm_pipe.execute(conn_tuple, create_conn.pipe_memory('path')):
                    sys.stdout.write("line no: " + str(cm_pipe.pipe_memory('line_num')) + "\r")
                sys.stdout.write("\n")

order = counters.keys()
for date in order:
    print "in data %s:" % date
    for ws in counters[date]:
        print "  ws '%s'" % ws
        for method in counters[date][ws]:
            print "    metodo '%s'" % method