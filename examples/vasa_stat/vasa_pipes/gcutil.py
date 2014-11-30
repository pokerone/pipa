
import pipa
import collections

#--------gcutil
def make_items_from_gcutil(inputlist):
    for input in inputlist:
        gc_util_tuple= collections.namedtuple("GCUtilTuple", "timestamp,S0,S1,E,O,P,YGC,YGCT,FGC,FGCT,GCT")
        input = input.line.strip(' \t\n\r')
        try:
            if input[0].isdigit():
                fields = input.split()
                item = gc_util_tuple(timestamp=fields[0],
                                     S0=float(fields[1]),
                                     S1=float(fields[2]),
                                     E=float(fields[3]),
                                     O=float(fields[4]),
                                     P=float(fields[5]),
                                     YGC=int(fields[6]),
                                     YGCT=float(fields[7]),
                                     FGC=int(fields[8]),
                                     FGCT=float(fields[9]),
                                     GCT=float(fields[10]))
                yield item
        except ValueError as e:
            pipa.logger.error(e)
            pipa.logger.error(input)

gcutil_pipe = pipa.Pipeline()
gcutil_pipe.append( pipa.system.item.ReadFromFile )
gcutil_pipe.append( pipa.util.item.Memory, fields_names=['line_num'] )
gcutil_pipe.append( make_items_from_gcutil )

