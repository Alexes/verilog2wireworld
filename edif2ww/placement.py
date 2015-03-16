'''
    EDIF2WW project file.
    Placement part of Place-and-Route stage of Verilog-to-Wireworld transformation.
'''

import wireworld as ww
import wireworld_lpm_tile6 as lpm

def do_placement(instances, nets, input_port_instance_names):
    ### divide instances into cascades
    fan_in_enable_counts = {} # holds the count of "enabled" in-edges for each vertex
    visited_vertices = {}
    current = list(input_port_instance_names) # a copy
    newCurrent = []
    cascades = []
    
    while True:
        cascades.append(list(current))
        for x in current:
            visited_vertices[x] = True
            adjs = _get_adjacent(nets, x)
            for adj in adjs: # find neighbors which have all inputs 'enabled'
                if (adj in visited_vertices):
                    continue
                    
                if (adj not in fan_in_enable_counts):
                    fan_in_enable_counts[adj] = 0
                
                fan_in_enable_counts[adj] += 1
                
                goal = instances[adj].get_fan_in_count()
                if (fan_in_enable_counts[adj] == goal):
                    newCurrent.append(adj)
    
        if (len(newCurrent) == 0):
            break
        current = newCurrent
        newCurrent = []
    
    tile_field = _place_cascades(instances, nets, cascades)
    
    return tile_field
    
def _get_adjacent(nets, instance_name):
    '''
        Returns list of names of instances connected to the instance_name.
    '''
    adjacents = []
    for net_name in nets:
        net = nets[net_name]
        candidates = []
        flag = False
        
        for (name, port) in net: # TODO is this legal?
            if (name != instance_name):
                candidates.append(name)
            if (name == instance_name):
                flag = True
        
        if (flag == True):
            for name in candidates:
                adjacents.append(name)
                
    return adjacents

import random
def _place_cascades(instances, nets, cascades):
    '''
        Places components divided into cascades.
        Determines the optimal ordering of components inside each cascade.
        Ordering of cascades is fixed and as is passed in the list.
    '''
    width = len(instances) * 9 + 9 # will make it wiser, I promise
    height = width
    tile_field = ww.TileLevelWireWorldUniverse(width = width, height = height)

    offset_row = 9
    offset_col = 3
    print 'WARNING: Randomly shuffling components within cascades'
    for cascade in cascades:
        random.shuffle(cascade)
        for inst_name in cascade:
            inst = instances[inst_name]
            tile_field.place_component(row = offset_row, col = offset_col, component = inst)
            inst.set_pos_in_tiles(row = offset_row, col = offset_col)
            offset_row += 9
            
        offset_col += 9
        offset_row = 9
    
    
    return tile_field
    