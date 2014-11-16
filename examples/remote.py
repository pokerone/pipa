
import collections
import pipa

import sys

def make_item_for_paramiko(item):
    new_item = collections.namedtuple("ParamikoInput", "host, user, pwd, key_path, path")
    user =''
    pwd = ''
    key_path=''
    if "@" in item.netloc:
        user=item.netloc.split("@")[0]
        address=item.netloc.split("@")[1]
        if ":" in user:
            pwd=user.split(":")[1]
            user=user.split(":")[0]
        if ":" in address:
            address = address[:-1]
    else:
        address = item.netloc
    return new_item(host=address, user=user, pwd=pwd, key_path=key_path, path=item.path)



remote_pipe = pipa.Pipeline()
remote_pipe.add_item( pipa.util.item.ParseUrl )
remote_pipe.add_item( pipa.util.item.Memory, fields_names=['netloc','path'] )
remote_pipe.add_item( pipa.util.item.MakeItem, func=make_item_for_paramiko )
remote_pipe.add_item( pipa.system.remote.ParamikoSSHConnection )
