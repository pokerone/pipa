
__author__ = 'andrea'

from pipa import PipelineItem

class LessThen(PipelineItem):

    def __init__(self, *args, **kwargs):
        super(LessThen, self).__init__(*args, **kwargs)
        self.name = 'less_then'
        self.tuple_name = 'less_then'

    def generator(self, tuples, field_name, reference_value=None):
        for tuple in tuples:
            field_value = getattr(tuple, field_name, None)
            if field_value and reference_value:
                if field_value < reference_value:
                    yield tuple
                else:
                    print "skipped line"

class GreaterThen(PipelineItem):

    def __init__(self, *args, **kwargs):
        super(GreaterThen, self).__init__(*args, **kwargs)
        self.name = 'greater_then'
        self.tuple_name = 'greater_then'

    def generator(self, tuples, field_name, value=None):
        for tuple in tuples:
            #print "sono GreaterThen: ", tuple

            if value != None:
                try:
                    field_value = getattr(tuple, field_name, None)
                    if field_value:
                        print field_value, value
                        if field_value > value:
                            yield tuple
                        else:
                            print "skipped line"
                except:
                    print "exception: skipped line"


class Select(PipelineItem):
    def __init__(self, *args, **kwargs):
        super(Select, self).__init__(*args, **kwargs)
        self.name = 'select'
        self.tuple_name = 'select'

    def generator(self, tuples, field_name='', func=None):
        for tuple in tuples:
            #print "sono GreaterThen: ", tuple
            self.logger.debug("select field name %s" % field_name)
            try:
                value = getattr(tuple, field_name, None)
                if func:
                    value = func(value)
                yield value
            except:
                print "exception: skipped line"
