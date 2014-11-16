

import linecache

from pipa import PipelineItem

class ReadFromFile(PipelineItem):

    def __init__(self, *args, **kwargs):
        super(ReadFromFile, self).__init__(*args, **kwargs)
        self.name = 'read_from_file'
        self.tuple_name = 'read_from_file'
        self.tuple_fields = 'line, tell, line_num, filename'
        self.start_from_line = kwargs.get('start_from_line', 0)
        self.start_from_tell = kwargs.get('start_from_tell', 0)

    def generator(self, files_list, start_from_tell=0, start_from_line=0, **kwargs):
        #TODO:perche' non vengono passati i parametri corretti?
        if start_from_line != 0:
            sfl = start_from_line
        else:
            sfl = self.start_from_line

        for file_tuple in files_list:
            self.logger.debug("Reading from '%s'" % file_tuple.path)
            file = file_tuple.file_obj

            line_num = 0
            #start from requested position
            file.seek(start_from_tell)
            #start from requested line
            for _ in xrange(sfl):
                file.readline()
            line_num = sfl

            while True:
                line_tell = file.tell()
                line = file.readline()
                next_line_tell = file.tell()
                #EOF reached?
                if line_tell == next_line_tell:
                    break
                line_num += 1
                yield self.make_item( line=line, tell=line_tell, line_num=line_num, filename=file_tuple.path )