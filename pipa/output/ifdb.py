
from influxdb import InfluxDBClient

from pipa import PipelineItem

class InfluxDbItem(PipelineItem):
    def __init__(self, *args, **kwargs):
        self.name = 'influx_db'
        self.user= kwargs.pop('user', 'guest')
        self.password= kwargs.pop('password', 'guest')
        self.host= kwargs.pop('host', '127.0.0.1')
        self.port= kwargs.pop('port', 8086)
        self.dbname= kwargs.pop('dbname', 'default')
        self.client = None
        super(InfluxDbItem, self).__init__(*args, **kwargs)

    def prepare(self):
        self.client = InfluxDBClient(host=self.host, port=self.port, username=self.user, password=self.password, dbname=self.dbname)

    def generator(self, tuple_list, **kwargs):
        for tuple in tuple_list:
            if tuple.type == 'insert':
                self.client.write_point(tuple.json_data)