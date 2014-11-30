
import collections
import json

import arrow
#--------create_db_item
def create_db_item(input_list, session_dict, group_points=1):
    db_item = collections.namedtuple("DbItem", "json_data")
    data = {}
    data['points'] = []
    data['columns'] = []
    for input in input_list:
        if input != None:
            data['name'] = session_dict['host'] + '.' + type(input).__name__
            temp_data = {}
            points = []
            for field_name in input._fields:
                temp_data[field_name] = getattr(input, field_name)
            for field_name, field_value in temp_data.iteritems():
                if field_name == 'timestamp':
                    field_name = 'time'
                if type(field_value).__name__ == 'Arrow':
                    field_value = float(field_value.timestamp)
                if field_name == 'time':
                    try:
                        field_value = float(field_value)
                    except:
                        print field_value

                data['columns'].append(field_name)
                if type(field_value) == type([]):
                    for value in field_value:
                        points.append(value)
                else:
                    points.append(field_value)

            #modify or add some general field
            for field_name in "item_creation_timestamp,host,session_id".split(","):
                if field_name == 'item_creation_timestamp':
                    data['columns'].append(field_name)
                    points.append(arrow.now().timestamp)
                if field_name == 'host':
                    data['columns'].append(field_name)
                    points.append(session_dict['host'])
                if field_name == 'session_id':
                    data['columns'].append(field_name)
                    points.append("_".join([session_dict['session_name'], str(session_dict['start_monitoring_time'].timestamp)]))
            data['points'].append(points)
            if len(data['points']) == group_points:
                yield json.dumps([data])

