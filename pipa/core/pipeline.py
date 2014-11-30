
import copy
import logging
from collections import namedtuple
from types import FunctionType


import log

class PipelineItem(object):
    def __init__(self, *args, **kwargs):
        super(PipelineItem, self).__init__()
        try:
            self.callable = args[0]
            self.generator = self.callable
            self.name = kwargs.pop('_item_name', self.callable.__name__)
        except IndexError as e:
            # no callable passed as parameter:
            # this is a subclassed PipelineItem, with a "generator" method overwritten
            self.name = kwargs.pop('_item_name', self.__class__.__name__ )
        self.callable_args = args
        self.callable_kwargs = kwargs
        self.pipeline_instance = None
        self.tuple_name = 'UNNAMED_TUPLE'
        self.tuple_fields = ''

        self.logger = logging.getLogger(".".join([log.logger_name, self.name]))

    def make_tuple(self, *args, **kwargs):
        nm = namedtuple(self.tuple_name, self.tuple_fields)(**kwargs)
        return nm

    def configure(self):
        return True

    def prepare(self):
        return True

class PipelineItemException(Exception):
    def __init__(self, error_code, message):
        self.message = message
        self.error_code = error_code
    def __str__(self):
        return repr(self.message)

class Pipeline(object):
    def __init__(self, *args, **kwargs):
        super(Pipeline, self).__init__()
        self.item_list = []
        self.logger = logging.getLogger(".".join([log.logger_name, self.__class__.__name__]))

    def append(self, item_to_add, **kwargs):
        if type(item_to_add) != FunctionType and issubclass(item_to_add,PipelineItem):
            i = item_to_add(**kwargs)
            i.pipeline_instance=self
            self.item_list.append(i)
            i.configure()
        else:
            p_item = PipelineItem(item_to_add, **kwargs)
            p_item.pipeline_instance=self
            self.item_list.append(p_item)


    def configure_item(self, item_name, **kwargs):
        for item in self.item_list:
            if item_name == item.name:
                if kwargs != {}:
                    item.callable_kwargs.update(kwargs)

    def execute(self, *args, **kwargs):
        chain = None
        new_kwargs = {}
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
        try:
            #merge the kwargs defined with the pipeline and the kwargs specified when called
            new_kwargs.update(first_item.callable_kwargs )
            new_kwargs.update( kwargs )
            chain = first_item.generator(first_iterable, *arguments, **new_kwargs)
        except TypeError, e:
            self.logger.error('Failed chain for "%s" item: "%s"' % (first_item.name,e))
            raise StopIteration
        try:
            #prepare the generator
            for item in execution_order:
                item.prepare()
            #chain the generators
            for item in execution_order:
                chain = item.generator(chain, **item.callable_kwargs)
        except PipelineItemException as e:
            self.logger.error('Failed chain for "%s" item: "%s"' % (first_item.name,e))
            raise StopIteration
        except TypeError, e:
            self.logger.error('Failed chain for "%s" item: "%s"' % (item.name,e))
            raise StopIteration
        #plase generate!
        generator = chain
        for item in generator:
            yield item