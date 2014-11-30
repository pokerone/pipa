
import collections
import pipa

import sys

def make_item_for_paramiko(item):
    new_tuple = collections.namedtuple("ParamikoInput", "host, user, pwd, key_path, path")
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
    return new_tuple(host=address, user=user, pwd=pwd, key_path=key_path, path=item.path)



create_conn= pipa.Pipeline()
create_conn.append( pipa.util.item.ParseUrl )
create_conn.append( pipa.util.item.Memory, fields_names=['netloc','path'] )
#create_conn.append( pipa.util.item.ConfigureItem, name='open_remote_file', item_kwargs={'remote_file':create_conn.pipe_memory('path')} )
create_conn.append( pipa.util.item.MakeItem, func=make_item_for_paramiko )
create_conn.append( pipa.system.remote.ParamikoSSHConnection )

