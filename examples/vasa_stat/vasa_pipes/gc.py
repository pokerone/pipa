
import collections

import pipa

#--------gc
def make_items_from_gc(input):
    gc_tuple= collections.namedtuple("GCTuple", "timestamp,S0C,S1C,S0U,S1U,EC,EU,OC,OU,PC,PU,YGC,YGCT,FGC,FGCT,GCT")
    try:
        input = input.line.strip(' \t\n\r')
        if input[0] != 'T' and int(input[0]) < 10:
            fields = input.split()
            item = gc_tuple(timestamp=fields[0],
                                 S0C=int(fields[1].split(".")[0])*1024,
                                 S1C=int(fields[2].split(".")[0])*1024,
                                 S0U=int(fields[3].split(".")[0])*1024,
                                 S1U=int(fields[4].split(".")[0])*1024,
                                 EC=int(fields[5].split(".")[0])*1024,
                                 EU=int(fields[6].split(".")[0])*1024,
                                 OC=int(fields[7].split(".")[0])*1024,
                                 OU=int(fields[8].split(".")[0])*1024,
                                 PC=int(fields[9].split(".")[0])*1024,
                                 PU=int(fields[10].split(".")[0])*1024,
                                 YGC=int(fields[11]),
                                 YGCT=int(fields[12].split(".")[0]),
                                 FGC=int(fields[13]),
                                 FGCT=int(fields[14].split(".")[0]),
                                 GCT=int(fields[15].split(".")[0]))
            return item
    except ValueError as e:
        pipa.logger.error( e )
        pipa.logger.error( input )


gc_pipe = pipa.Pipeline()
gc_pipe.append( pipa.system.item.ReadFromFile )
gc_pipe.append( pipa.util.item.Memory, fields_names=['line_num'] )
gc_pipe.append( pipa.util.item.MakeItem, func=make_items_from_gc )

