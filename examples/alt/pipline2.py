
import copy
import pipa

class Pipeline(pipa.Pipeline):
    def __init__(self, *args, **kwargs):
        super(Pipeline, self).__init__(*args, **kwargs)

    def execute(self, *args, **kwargs):
        arguments = [arg for arg in args]
        execution_order= copy.copy(self.item_list)

        first_item = execution_order.pop(0)
        first_item.prepare()

        try:
            first_iterable = arguments.pop(0)
            if type(first_iterable) != type([]):
                first_iterable = [ first_iterable ]
        except IndexError:
            first_iterable = []

        chain = first_item.generator(first_iterable, *arguments, **kwargs)
        try:
            #prepare the generator
            for item in execution_order:
                item.prepare()
            #chain the generators
            for item in execution_order:
                chain = item.generator(chain, **item.callable_kwargs)
        except pipa.PipelineItemException as e:
            print e
        #plase generate!
        generator = chain
        for item in generator:
            yield item