'''
    EDIF2WW project file.
    Implements the routing part of the Place-&-Route process.
'''

#import wireworld as ww # what about multiple import?

def do_routing(tile_field, nets, instances):
    '''
        tile_field - wireworld.TileLevelWireWorldUniverse instance (need to import?)
        nets - dict of nets as their names as keys
        instances - dict of LPM and other instances with their names as keys
        
        Function performs operations on tile_field in place.
    '''
    for net_name in nets:
        net = nets[net_name]
        if (len(net) != 2):
            raise RuntimeError('Routing error: currently only 2-terminal nets are supported')
        if (net[0][0] == 'None' or net[1][0] == 'None'):
            print 'TODO: currently not routing design ports'
            continue
        wave_route_wire(tile_field, instances, net_name, nets[net_name])
        
        
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
    
    inst_b_name = net[1][0]
    inst_b = instances[inst_b_name]
    inst_b_port_name = net[1][1]
    inst_b_pos = inst_b.get_pos_in_tiles()
    port_b_local_pos = inst_b.get_port_local_tile_pos(inst_b_port_name)
    port_b_global_pos = _add_coords( inst_b_pos, port_b_local_pos )
    
    ## starting wave algo
    start = port_a_global_pos
    dest = port_b_global_pos
    
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
        neighs = _get_passable_neighs(fld, cur[0], cur[1])
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
            neighs = _get_passable_neighs(fld, cur[0], cur[1]) # TODO maybe remove passability condition?
            predating_neighs = [n for n in neighs if dist[n[0]][n[1]] == cur_dist-1]
            cur = predating_neighs[0]
            
def _get_passable_neighs(fld, row, col):
    '''
        Returns a list of tuples with coords of
        passable von Neumann neighbors.
    '''
    neighs = []
    if (row > 0 and fld.get(row-1, col) == ' '):
        neighs.append( (row-1, col) )
    if (col > 0 and fld.get(row, col-1) == ' '):
        neighs.append( (row, col-1) )
    if (row < fld.get_height()-1 and fld.get(row+1, col) == ' '):
        neighs.append( (row+1, col) )
    if (col < fld.get_width()-1 and fld.get(row, col+1) == ' '):
        neighs.append( (row, col+1) )
    return neighs
    
def _add_coords(a, b):
    '''
        a,b - tuples (row, col).
        Performs vector addition of two given tuples.
    '''
    return (a[0] + b[0], a[1] + b[1])