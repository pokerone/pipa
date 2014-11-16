

import os
import fnmatch

import paramiko
from pipa import PipelineItem

class OpenFiles(PipelineItem):
    def __init__(self, *args, **kwargs):
        super(OpenFiles, self).__init__(*args, **kwargs)
        self.name='open_remote_files'
        self.tuple_name = 'open_remote_files'
        self.tuple_fields = 'connection, path, file_obj'

    def generator(self, paramiko_conns):
        for conn in paramiko_conns:
            sftp_client = conn.connection.open_sftp()
            file_obj = sftp_client.file(conn.filename,'r')
            yield self.make_item(connection=conn.connection, file_obj=file_obj, path=conn.filename)
            file_obj.close()
            sftp_client.close()