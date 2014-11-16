
import sys
import collections

import pipa

def grep_in_line(file_tuples, grep='', search_in='line'):
    fields_to_check = [search_in]
    txt_to_grep = grep.split(',')
    if "," in 'search_in':
        fields_to_check = search_in.split(",")
    for tuple in file_tuples:
        for field in fields_to_check:
            field_value = getattr(tuple, field, None)
            if field_value != None:
                for grep in txt_to_grep:
                    if grep in field_value:
                        yield tuple

def make_items_from_file(input):
    file_tuple = collections.namedtuple("FileTuple", "path, file_obj")
    item = file_tuple(path=input.name, file_obj=input)
    print item
    return item

def group_by_method_pu(tuples):
    method_dict={}
    filename_dict={}
    readed_tuples = 0
    last_filename = ''
    for tuple in tuples:
        readed_tuples += 1
        sys.stdout.write("Parsed %s event from %s   \r" % (readed_tuples, tuple.filename ) )
        if last_filename != tuple.filename:
            sys.stdout.write("\n")
            readed_tuples = 0
        sys.stdout.flush()
        last_filename = tuple.filename
        filename_dict[tuple.filename] = 0
        line = tuple.line.split(" ")[5]
        method = line.split(".")[1][:-1]
        try:
            method_dict[method] += 1
        except KeyError:
            method_dict[method] = 1
    days = len(filename_dict.keys())
    sec_num = float(60*60*24) * days
    min_num = float(60*24) * days
    print "Parsed %s days" % days
    for k,v in method_dict.iteritems():
        v=float(v)
        yield "'%s'     : tot: %s, al sec: %f, al min: %f " % (k, v, v/sec_num, v/min_num)

pu_pipe=pipa.Pipeline()
pu_pipe.add_item(pipa.system.find_in_path)
pu_pipe.add_item(pipa.system.open_files)
pu_pipe.add_item(pipa.util.item.MakeItem, func=make_items_from_file)
pu_pipe.add_item(pipa.util.item.Memory, fields_names=['path'])
pu_pipe.add_item(pipa.system.item.ReadFromFile)
pu_pipe.add_item(grep_in_line, grep='addNote,checkCap,deleteUserProfile,deleteSubscriptionById,getCatalog,getInterestList,getProfessionList,getQualificationList,getUserInfo,getUserInfoEx,subscribe,update,updateSubscriptionById,updateSubscriptions,updateUserProfile,pullOutMsisdn,updateUserProfileNVL,setAssentList,getAssentList')
pu_pipe.add_item(grep_in_line, grep='FreetimeWs')
pu_pipe.add_item(group_by_method_pu)

#------------------per freetime
def group_by_method_fex(tuples):
    method_dict={}
    filename_dict={}
    for tuple in tuples:
        filename_dict[tuple.filename] = 0
        method = tuple.line.split(" ")[6][1:-1]
        if not method[0].isdigit():
            try:
                method_dict[method] += 1
            except KeyError:
                method_dict[method] = 1
        else:
            print "error with line: '%s'" % tuple.line.strip(" \t\r\n")

    days = len(filename_dict.keys())
    sec_num = float(60*60*24) * days
    min_num = float(60*24) * days
    print "Parsed %s days" % days
    for k,v in method_dict.iteritems():
        v=float(v)
        yield "'%s'     : tot: %s, al sec: %f, al min: %f " % (k, v, v/sec_num, v/min_num)

ft_pipe=pipa.Pipeline()
ft_pipe.add_item(pipa.system.find_in_path)
ft_pipe.add_item(pipa.system.open_files)
ft_pipe.add_item(pipa.util.item.MakeItem, func=make_items_from_file)
ft_pipe.add_item(pipa.util.item.Memory, fields_names=['path'])
ft_pipe.add_item(pipa.system.item.ReadFromFile)
ft_pipe.add_item(grep_in_line, grep='FreetimeExSkeleton')
ft_pipe.add_item(grep_in_line, grep='INFO')
ft_pipe.add_item(group_by_method_fex)
