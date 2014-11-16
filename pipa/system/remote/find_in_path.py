
import os
import fnmatch

from pipa import PipelineItem

class FindInPath(PipelineItem):
    def __init__(self, *args, **kwargs):
        super(FindInPath, self).__init__(*args, **kwargs)
        self.name='find_in_remote_path'
        self.tuple_name = 'find_in_remote_path'
        self.tuple_fields = 'connection, filename'

    def generator(self, paramiko_conns, path='', filemask='', **kwargs):
        for conn in paramiko_conns:
            sftp_client = conn.connection.open_sftp()
            file_list = sftp_client.listdir(path=path)
            for name in fnmatch.filter(file_list, filemask):
                yield self.make_item(connection=conn.connection, filename=os.path.join(path,name))
            sftp_client.close()