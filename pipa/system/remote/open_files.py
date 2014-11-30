

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

    def generator(self, paramiko_conns, file_to_open=''):
        for conn in paramiko_conns:
            sftp_client = conn.connection.open_sftp()
            self.logger.debug("Try to open: %s" % file_to_open)
            try:
                file_obj = sftp_client.file(file_to_open,'r')
                yield self.make_tuple(connection=conn.connection, file_obj=file_obj, path=file_to_open)
                file_obj.close()
            except IOError as e:
                self.logger.debug(e)
            sftp_client.close()