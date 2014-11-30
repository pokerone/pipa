
import pipa
from parse_jpig_lines import parse_line

cm_pipe= pipa.Pipeline()
cm_pipe.append(pipa.system.remote.ReadFromFile)
cm_pipe.append(pipa.processing.filters.Grep, field_name='line', value='Frontend', options='v')
cm_pipe.append( pipa.util.item.Memory, fields_names=['line_num'] )
cm_pipe.append( parse_line, result_dict={} )
