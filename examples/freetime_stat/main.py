
import os

import pipe

def parse_pu_log():

    conn_string=[   "c:\\temp\\lavoro\\mille\\144\\server.log.2014-11-*",
                    "c:\\temp\\lavoro\\mille\\145\\server.log.2014-11-*"]
    for conn in conn_string:
        for line in pipe.pu_pipe.execute(root=os.path.dirname(conn), find=os.path.basename(conn)):
            print line

def parse_freetime_log():

    conn_string=[   "c:\\temp\\lavoro\\mille\\136\\freetimeex.log.2014-11-*",
                    "c:\\temp\\lavoro\\mille\\137\\freetimeex.log.2014-11-*"    ]
    for conn in conn_string:
        for line in pipe.ft_pipe.execute(root=os.path.dirname(conn), find=os.path.basename(conn)):
            print line

def main():
    parse_pu_log()

main()