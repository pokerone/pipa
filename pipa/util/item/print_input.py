
from pipa import PipelineItem

class PrintInput(PipelineItem):
    def generator(self, input_list):
        for input in input_list:
            print input