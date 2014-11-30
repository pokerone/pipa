
from urlparse import urlparse

from pipa import PipelineItem

class ParseUrl(PipelineItem):

    def __init__(self, *args, **kwargs):
        super(ParseUrl, self).__init__(*args, **kwargs)
        self.name='parse_url'

    def generator(self, address_list):
        for address in address_list:
            t = urlparse(address)
            print t
            yield t