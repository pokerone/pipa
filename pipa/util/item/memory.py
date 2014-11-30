
from pipa import Pipeline
from pipa import PipelineItem

class Memory(PipelineItem):
    def __init__(self, *args, **kwargs):
        super(Memory, self).__init__(*args, **kwargs)
        self.name='memory'
        self.field_to_save=kwargs.get('fields_names', [])

    def configure(self):
        if not hasattr(self.pipeline_instance, 'pipeline_memory'):
            setattr(self.pipeline_instance, 'pipeline_memory', {})
        for field in self.field_to_save:
            self.pipeline_instance.pipeline_memory[id(self.pipeline_instance)] = {field:''}
        Pipeline.pipe_memory = get_from_memory_property

    def generator(self, item_list, fields_names = [] ):
        for item in item_list:
            self.logger.debug(item)
            for field in fields_names:
                field_name = field
                if ":" in field:
                    field_name = field.split(":")[1]
                    field = field.split(":")[0]
                field_value = getattr(item,field)
                if field_value != None:
                    try:
                        pipe_memory = self.pipeline_instance.pipeline_memory[id(self.pipeline_instance)]
                        pipe_memory[field_name] = field_value
                    except KeyError as e:
                        self.pipeline_instance.pipeline_memory[id(self.pipeline_instance)] = {field_name:field_value}
            yield item

def get_from_memory_property(self, field_name):
    value = None
    try:
        value = self.pipeline_memory[id(self)][field_name]
    except KeyError as e:
        pass
    return value