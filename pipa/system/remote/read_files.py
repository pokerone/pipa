
import os
import urlparse
import paramiko


import pipa
from pipa import PipelineItem

class ReadFromFile(PipelineItem):

    def __init__(self, *args, **kwargs):
        super(ReadFromFile, self).__init__(*args, **kwargs)
        self.name='read_from_file'
        self.tuple_name = 'remote_file'
        self.tuple_fields = 'line, tell, line_num, filename'
        #self.start_from_line = kwargs.get('start_from_line', 0)
        #self.start_from_tell = kwargs.get('start_from_tell', 0)

    def generator(self, paramiko_connections, path='', start_from_tell=0, start_from_line=0, **kwargs):

        for conn in paramiko_connections:
            file_list =[]
            if path != '' or path != None and len(path) > 0:
                sftp_client = conn.connection.open_sftp()
                if '*' in path:
                    filename = os.path.basename(path)
                    dirname = os.path.dirname(path)
                    left_string, right_string = filename.split('*')
                    for file in sftp_client.listdir(path=dirname):
                        if left_string in file and right_string in file:
                            file_list.append( "/".join([dirname, file]) )
                else:
                    file_list.append(path)
                for f in file_list:
                    print "open file '%s'" % f
                    remote_file = sftp_client.open(f, 'rb')
                    line_num = 0
                    line=''
                    while True:
                        try:
                            line_tell = remote_file.tell()
                            line = remote_file.readline()
                            next_line_tell = remote_file.tell()
                            if line_tell == next_line_tell:
                                break
                            line_num += 1
                            item =  self.make_tuple( line=line, tell=line_tell, line_num=line_num, filename=f )
                            yield item
                        except UnicodeDecodeError as e:
                            print e


