

import pipa
from pipa import PipelineItem

class MakeItem(PipelineItem):
    def __init__(self, *args, **kwargs):
        super(MakeItem, self).__init__(*args, **kwargs)
        self.name = 'make_item'

    def generator(self, input_list, func=None, func_kwargs={}):
        for input in input_list:
            item = func(input, **func_kwargs)
            self.logger.debug(item)
            yield item