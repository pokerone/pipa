

def parse_line(tuples, result_dict={}, errors_dict={}):
    for tuple in tuples:
        line_array=tuple.line.strip(" \r\t\n").split(" ")
        date=line_array[0]
        partner = line_array[7][1:-1].split("_", 1)[0]
        ws=line_array[8][1:-1]
        method=line_array[9][1:-1]
        return_code = line_array[10][1:-1]
        time=line_array[11][1:-1]
        result=line_array[13]
        try:
            values = result_dict[date][ws][method][partner]
            if values != []:
                values[0] += 1
            else:
                result_dict[date][ws][method][partner] = [1,0,0,0]
        except IndexError:
            print "it is an autovivification dict?"
        yield tuple