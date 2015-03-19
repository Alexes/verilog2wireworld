'''
    EDIF2WW project file.
    Implements the routing part of the Place-&-Route process.
'''

#import wireworld as ww # what about multiple import?

def do_cascade_routing(tile_field, nets, instances, cascades):
    '''
        tile_field - wireworld.TileLevelWireWorldUniverse instance (need to import?)
        nets - dict of nets as their names as keys
        instances - dict of LPM and other instances with their names as keys
        
        Function performs operations on tile_field in place.
    '''
    # divide nets into cascades as well
    net_cascades = []
    for cascade in cascades:
        net_cascade = []
        for inst_name in cascade:
            net_cascade += _find_incoming_nets(nets, instances[inst_name])
        net_cascades.append(list(net_cascade))
    
    # route nets according to the order
    for net_cascade in net_cascades:
        for net_name in net_cascade:
            net = nets[net_name]
            if (len(net) != 2):
                raise RuntimeError('Routing error: currently only 2-terminal nets are supported')
            wave_route_wire(tile_field, instances, net_name, nets[net_name])
        
def _find_incoming_nets(nets, inst):
    result = []
    input_port_names = inst.get_input_port_names()
    inst_name = inst.get_name()
    
    for net_name in nets:
        net = nets[net_name]
        for endpoint in net:
            if (endpoint[0] == inst_name and endpoint[1] in input_port_names):
                result.append(net_name)
    
    return result

def wave_route_wire(fld, instances, net_name, net):
    '''
        Performs Wave propagation algorithm
        and draws a WireWorld conductor wire between
        terminals given in 'net' paremeter in format:
        [(inst_name, port_name), (inst_name, port_name), ...].
    '''
    ## calculating start and destination global coordinates in tile space
    inst_a_name = net[0][0]
    inst_a = instances[inst_a_name]
    inst_a_port_name = net[0][1]
    inst_a_pos = inst_a.get_pos_in_tiles()
    port_a_local_pos = inst_a.get_port_local_tile_pos(inst_a_port_name)
    port_a_global_pos = _add_coords( inst_a_pos, port_a_local_pos )
    port_a_full_name = inst_a_name + '.' + inst_a_port_name
    
    inst_b_name = net[1][0]
    inst_b = instances[inst_b_name]
    inst_b_port_name = net[1][1]
    inst_b_pos = inst_b.get_pos_in_tiles()
    port_b_local_pos = inst_b.get_port_local_tile_pos(inst_b_port_name)
    port_b_global_pos = _add_coords( inst_b_pos, port_b_local_pos )
    port_b_full_name = inst_b_name + '.' + inst_b_port_name
    
    ## passable labels for this net
    passable_tile_labels = [' ', port_a_full_name, port_b_full_name]
    
    ## starting wave algo
    start = port_a_global_pos
    dest = port_b_global_pos
    if (fld.get(start[0], start[1]) not in passable_tile_labels):
        print 'Routing error - one of the terminals of net "' + net_name + '" is occupied by something with label "' + str(fld.get(start[0], start[1])) + '". Cannot route it.'
        return
    if (fld.get(dest[0], dest[1]) not in passable_tile_labels):
        print 'Routing error - one of the terminals of net "' + net_name + '" is occupied by something with label "' + str(fld.get(dest[0], dest[1])) + '". Cannot route it.'
        return
    
    # creating a copy of the field to store distances (should move this out of this function)
    UNVISITED = -1
    dist = [[UNVISITED for col in range(fld.get_width())] for row in range(fld.get_height())]
    dist[start[0]][start[1]] = 0

    # setting the wave off
    wavefront = [start]
    reached = False
    while True:
        # check if unprocessed wavefront cells left
        if (len(wavefront) == 0):
            print 'Routing error - Ports planarly unreachable:', inst_a_name+'.'+inst_a_port_name, 'and', inst_b_name+'.'+inst_b_port_name
            reached = False
            break
        
        # check if current cell is the destination
        cur = wavefront.pop()
        if (cur[0] == dest[0] and cur[1] == dest[1]):
            reached = True
            break
            
        # get passable unvisited neighbors
        neighs = _get_passable_neighs(fld, cur[0], cur[1], passable_tile_labels)
        unvisited_neighs = [n for n in neighs if dist[n[0]][n[1]] == UNVISITED]
        
        # expand the wave
        for n in unvisited_neighs:
            dist[n[0]][n[1]] = dist[cur[0]][cur[1]] + 1
        wavefront = unvisited_neighs + wavefront # BFS way
        
    # backtracing the wire
    if (reached):
        cur = dest
        while True:
            # drawing conductor
            fld.place_conductor(cur[0], cur[1], net_name)
            
            # check if we reached the start
            if (cur[0] == start[0] and cur[1] == start[1]):
                break
            
            # deciding where to go next
            cur_dist = dist[cur[0]][cur[1]]
            neighs = _get_passable_neighs(fld, cur[0], cur[1], passable_tile_labels) # TODO maybe remove passability condition?
            predating_neighs = [n for n in neighs if dist[n[0]][n[1]] == cur_dist-1]
            if (len(predating_neighs) == 0):
                print 'Routing error - one of the net terminals is occupied by something'
                break
            else:
                cur = predating_neighs[0]
            
def _get_passable_neighs(fld, row, col, passable_tile_labels):
    '''
        Returns a list of tuples with coords of
        passable von Neumann neighbors.
        
        Net port names are needed so that components' port connection locations can be made
        passable for the currently created route.
    '''
    neighs = []
    if (row > 0 and fld.get(row-1, col) in passable_tile_labels):
        neighs.append( (row-1, col) )
    if (col > 0 and fld.get(row, col-1) in passable_tile_labels):
        neighs.append( (row, col-1) )
    if (row < fld.get_height()-1 and fld.get(row+1, col) in passable_tile_labels):
        neighs.append( (row+1, col) )
    if (col < fld.get_width()-1 and fld.get(row, col+1) in passable_tile_labels):
        neighs.append( (row, col+1) )
    return neighs
    
def _add_coords(a, b):
    '''
        a,b - tuples (row, col).
        Performs vector addition of two given tuples.
    '''
    return (a[0] + b[0], a[1] + b[1])