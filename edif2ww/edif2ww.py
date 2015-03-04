''' 
    Command line tool to transform netlists in EDIF (LPM) format to WireWorld layout in Extended RLE format.
'''

def dispatch(stmt, params=[]):
    '''
        EDIF parsing routine.
    '''
    stmt = stmt.lower()

    if (stmt == 'edif'):
        t = {'stmt':'edif', 'libraries':{}, 'design':None}
        if (type(params[0]) is str):
            t['name'] = params[0]
        else:
            print 'EDIF syntax error: Statement "edif" - name should follow the statement'
            
        for p in params:
            if (type(p) is dict and p['stmt'] == 'library'):
                t['libraries'][p['name']] = p
            if (type(p) is dict and p['stmt'] == 'design'):
                if (t['design'] != None): print 'EDIF parsing problem: expected only one "design" inside "edif" but got more than one'
                t['design'] = p
        return t

    elif (stmt == 'library' or stmt == 'external'):
        t = {'stmt':'library', 'name':params[0], 'cells':{}}
        for p in params:
            if (type(p) is dict and p['stmt'] == 'cell'):
                t['cells'][p['name']] = p
        return t

    elif (stmt == 'cell'):
        t = {'stmt':'cell', 'name':params[0], 'views':{}}
        for p in params:
            if (type(p) is dict and p['stmt'] == 'view'):
                t['views'][p['name']] = p
        return t

    elif (stmt == 'view'):
        t = {'stmt':'view', 'name':params[0]}
        for p in params:
            if (type(p) is dict and p['stmt'] == 'viewtype' and p['value'].upper() != 'NETLIST'): # removing all the views except NETLISTs
                return None
            if (type(p) is dict and p['stmt'] == 'viewtype' and p['value'].upper() == 'NETLIST'):
                t['viewtype'] = p['value'].upper()
            if (type(p) is dict and p['stmt'] == 'interface'):
                t['interface'] = p
            if (type(p) is dict and p['stmt'] == 'contents'):
                t['contents'] = p

        return t
    
    elif (stmt == 'viewtype'):
        t = {'stmt':'viewtype', 'value':params[0]}
        return t
            
    elif (stmt == 'interface'):
        t = {'stmt':'interface', 'ports':{}, 'properties':{}}
        for p in params:
            if (type(p) is dict and p['stmt'] == 'port'):
                t['ports'][p['name']] = p
            if (type(p) is dict and p['stmt'] == 'property'):
                t['properties'][p['name']] = p
        return t

    elif (stmt == 'port'):
        t = {'stmt':'port', 'name':params[0]}
        for p in params:
            if (type(p) is dict and p['stmt'] == 'direction'):
                t['direction'] = p['value']
        return t
    elif (stmt == 'direction'):
        t = {'stmt':'direction', 'value':params[0].upper()}
        return t
    
    elif (stmt == 'property'):
        t = {'stmt':'property', 'name':params[0].upper(), 'value':None}
        for p in params:
            if (type(p) is dict and (p['stmt'] == 'string' or p['stmt'] == 'integer')):
                t['value'] = p['value']
        return t
    elif (stmt == 'string'):
        t = {'stmt':'string', 'value':params[0].lstrip('"').rstrip('"')}
        return t
    elif (stmt == 'integer'):
        t = {'stmt':'integer', 'value':int(params[0])}
        return t

    elif (stmt == 'contents'):
        t = {'stmt':'contents', 'instances':{}, 'nets':{}}
        for p in params:
            if (type(p) is dict and p['stmt'] == 'instance'):
                t['instances'][p['name']] = p
            if (type(p) is dict and p['stmt'] == 'net'):
                t['nets'][p['name']] = p
        return t
    
    elif (stmt == 'libraryref'):
        t = {'stmt':'libraryref', 'name':params[0]}
        return t
    elif (stmt == 'cellref'):
        t = {'stmt':'cellref', 'name':params[0]}
        for p in params:
            if (type(p) is dict and p['stmt'] == 'libraryref'):
                t['library'] = p['name']
        return t
    elif (stmt == 'viewref'):
        t = {'stmt':'viewref', 'name':params[0]}
        for p in params:
            if (type(p) is dict and p['stmt'] == 'cellref'):
                t['cell'] = p['name']
                t['library'] = p['library']
        return t
    elif (stmt == 'instance'):
        t = {'stmt':'instance', 'name':params[0]}
        for p in params:
            if (type(p) is dict and p['stmt'] == 'viewref'):
                t['view'] = p['name']
                t['cell'] = p['cell']
                t['library'] = p['library']
        return t

    elif (stmt == 'net'):
        t = {'stmt':'net', 'name':params[0], 'joined_ports':[]}
        for p in params:
            if (type(p) is dict and p['stmt'] == 'joined'):
                if (t['joined_ports'] != []) : print 'EDIF syntax error: "net" statement should not have more than one "joined" statement inside'
                t['joined_ports'] = p['ports']
        return t
    elif (stmt == 'joined'):
        t = {'stmt':'joined', 'ports':[]}
        for p in params:
            if (type(p) is dict and p['stmt'] == 'portref'):
                t['ports'].append(p)
        return t
    elif (stmt == 'portref'):
        t = {'stmt':'portref', 'portname':params[0], 'instance':None}
        for p in params:
            if (type(p) is dict and p['stmt'] == 'instanceref'):
                t['instance'] = p['value']
        return t
    elif (stmt == 'instanceref'):
        t = {'stmt':'instanceref', 'value':params[0]}
        return t

    elif (stmt == 'design'):
        t = {'stmt':'design', 'name':params[0], 'cell':None, 'library':None}
        for p in params:
            if (type(p) is dict and p['stmt'] == 'cellref'):
                if (t['cell'] != None): print 'EDIF parsing problem: expected only one "cellRef" inside "design" but got more than one'
                t['cell'] = p['name']
                t['library'] = p['library']
        return t

    return None


### Parsing given EDIF file
import sys    
edif_file_path = sys.argv[1]
print 'Parsing', edif_file_path

import shlex
s = shlex.shlex( file(edif_file_path) )


state = 'NORMAL'
statementStack = []
valuesStack = []
token = s.get_token()
while (token != s.eof):
    if (state == 'WAITING_STATEMENT'):
        statementStack.append(token)
        state = 'NORMAL'
    elif (state == 'NORMAL' and token == '('):
        valuesStack.append(token)
        state = 'WAITING_STATEMENT'
    elif (state == 'NORMAL' and token == ')'):
        statement = statementStack.pop()
        params = []
        
        val = valuesStack.pop()
        while (val != '('):
            params.append(val)
            val = valuesStack.pop()
        
        params.reverse()
        returnVal = dispatch(statement, params)
        if (returnVal != None):
            valuesStack.append(returnVal)
        
    elif (state == 'NORMAL' and token not in ['(', ')']):
        valuesStack.append(token)
    
    token = s.get_token()
    

edif = valuesStack[0]
#print 'Evaluation result is', edif
### Done with parsing

### Processing netlist
design_library = edif['design']['library']
design_cell = edif['design']['cell']

design_views_dict = edif['libraries'][design_library]['cells'][design_cell]['views']
design_view = None
for key in design_views_dict:
    if (design_views_dict[key]['viewtype'] == 'NETLIST'):
        if (design_view != None):
            print 'ERROR: more than one NETLIST view found in design cell'
            exit()
        design_view = design_views_dict[key]
if (design_view == None):
    print 'ERROR: haven''t found NETLIST view in design cell'
    print 'Design library:', design_library
    print 'Design cell:', design_cell
    exit()


import wireworld_lpm_tile6 as lpm
print 'Performing technology mapping to WireWorld Tile algorithm of size 6'
print 'INSTANCES:'
component_instances = {}
# {name: LPM_AND_instance }
for key in design_view['contents']['instances']:
    instance = design_view['contents']['instances'][key]
    name = instance['name'] 
    library = instance['library']
    cellRef = instance['cell']
    viewRef = instance['view']
    
    LPM_cell_properties = edif['libraries']['LPM_LIBRARY']['cells'][cellRef]['views'][viewRef]['interface']['properties']
    lpm_type = LPM_cell_properties['LPM_TYPE']['value'] 
    lpm_size = LPM_cell_properties['LPM_SIZE']['value']
    lpm_width = LPM_cell_properties['LPM_WIDTH']['value']
    print (name + ': ' + lpm_type
        + '(SIZE=' + str(lpm_size) + ', WIDTH=' + str(lpm_width) + ')')
    
    # instantiating modules
    instance = None
    if (lpm_type == 'LPM_AND'):
        instance = lpm.LPM_AND(name, lpm_size, lpm_width)
    elif (lpm_type == 'LPM_OR'):
        instance = lpm.LPM_OR(name, lpm_size, lpm_width)
    else:
        raise RuntimeError('Incorrect or unimplemented type: ' + lpm_type)
    component_instances[name] = instance
    
print 'NETS:'
nets = {}
# {name: [('U1', 'Data0x0'), ('U2', 'Result0')]}
for key in design_view['contents']['nets']:
    net = design_view['contents']['nets'][key]
    net_name = net['name']
    nets[net_name] = []
    print net_name +':', 
    for i in range(len(net['joined_ports'])):
        inst_name = str(net['joined_ports'][i]['instance'])
        inst_port = net['joined_ports'][i]['portname']
        nets[net_name].append( (inst_name, inst_port) )
        print inst_name + '.' + inst_port, 
        if (i < len(net['joined_ports']) - 1): print '-',
    print
    
    
    
print 'Placing components...'
import wireworld as ww
import wireworld_lpm_tile6 as lpm

width = len(component_instances) * 9 # will make it wiser, I promise
height = width
tile_field = ww.TileLevelWireWorldUniverse(width = width, height = height)

cursor = 0
slots_per_row = len(component_instances)
for inst_name in component_instances:
    inst = component_instances[inst_name]
    row = int(cursor / slots_per_row) * 9 + 3
    col = int(cursor % slots_per_row) * 9 + 3
    tile_field.place_component(row = row, col = col, component = inst)
    inst.set_pos_in_tiles(row = row, col = col)
    cursor += 1

print 'Routing nets...'
import routing
routing.do_routing(tile_field, nets, component_instances)

print 'Writing RLE...'
import os
import rle_writer as rle
# converting tile-level universe into cell-level universe
cell_field = tile_field.write_cell_level_universe(instances_dict = component_instances, nets_dict = nets)
# preparing RLE filename and path
directory, edif_filename = os.path.split(edif_file_path)
filename, ext = os.path.splitext(edif_filename)
rle_filename = filename + '.rle'
rle_file_path = os.path.join(directory, rle_filename)
rle_file_path = os.path.normpath(rle_file_path)
# writing
rle.write_rle(rle_file_path, cell_field.get_field())
print 'Written RLE to', rle_file_path