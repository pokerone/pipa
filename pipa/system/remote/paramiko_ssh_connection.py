
import urlparse
import paramiko


import pipa
from pipa import PipelineItem

class ParamikoSSHConnection(PipelineItem):

    def __init__(self, *args, **kwargs):
        super(ParamikoSSHConnection, self).__init__(*args, **kwargs)
        self.name='ParamikoSSHConnection'
        self.tuple_name = 'paramiko_connection'
        self.tuple_fields = 'connection'

    def generator(self, connections, keys_path=''):
        for conn in connections:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(conn.host, username=conn.user, password=conn.pwd)
            yield self.make_item(connection=ssh)
            ssh.close()