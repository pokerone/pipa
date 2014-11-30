
import multiprocessing
import pipa
from pipa import PipelineItem



class ReadFromQueue(PipelineItem):

    def __init__(self, *args, **kwargs):
        super(ReadFromQueue, self).__init__(*args, **kwargs)

    def generator(self, queue):
        print multiprocessing.current_process()
        while True:
            obj = queue.get()
            yield obj

