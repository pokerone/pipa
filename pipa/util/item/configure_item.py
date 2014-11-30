
from pipa import PipelineItem

class ConfigureItem(PipelineItem):
    def __init__(self, *args, **kwargs):
        super(ConfigureItem, self).__init__(*args, **kwargs)

    def generator( self, iterable, name='', item_kwargs={} ):
        for tpl in iterable:
            self.pipeline_instance.configure_item(name, **item_kwargs)
            self.logger.debug(name, item_kwargs)
            yield tpl