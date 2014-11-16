
import collections

import pipa
from pipa import PipelineItem

class Remap(PipelineItem):
    def __init__(self, *args, **kwargs):
        super(Remap, self).__init__(*args, **kwargs)

    def generator(self, input_list, field_name='', func=None, func_kwargs={}):
        for input in input_list:
            item = None
            try:
                new_value = func(getattr(input, field_name, None), **func_kwargs)
                old_values = {}
                field_list = " ".join([f for f in input._fields])
                for f in input._fields:
                    old_values[f] = getattr(input, f)
                old_values[field_name] = new_value
                new_tuple = collections.namedtuple(type(input).__name__, field_list )
                item = new_tuple(**old_values)
            except AttributeError as e:
                print e
            yield item