
import pipa
import gzip, bz2

from logbook import Logger
logger=Logger(".".join([pipa.logger_name, __name__]))


class OpenFile(pipa.PipelineItem):

    def __init__(self, *args, **kwargs):
        super(OpenFile, self).__init__(*args, **kwargs)
        self.name = 'open_file'
        self.tuple_name = 'open_file'
        self.tuple_fields = 'file_obj'

    def generator(self, filenames, **kwargs):
        for name in filenames:
            print name
            if name.endswith(".gz"):
                #logger.debug("open %s" % name)
                file = gzip.open(name)
            elif name.endswith(".bz2"):
                #logger.debug("open %s" % name)
                file = bz2.BZ2File(name)
            else:
                #logger.debug("open %s" % name)
                file = open(name)
            yield self.make_item( file_obj=file )
            file.close()
