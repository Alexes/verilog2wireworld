'''
    EDIF2WW project file.
    Placement part of Place-and-Route stage of Verilog-to-Wireworld transformation.
'''

import wireworld as ww
import wireworld_lpm_tile6 as lpm
import wireworld_wires_library_tile6 as wires

def do_cascade_placement(instances, nets, input_port_instance_names):
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
    
    ### add feedthroughs for later-used ports
    _add_feedthroughs(instances, nets, cascades)
    
    ### 
    _find_optimal_intracascade_ordering(instances, nets, cascades)
    
    ### add crossings
    _add_crossings(instances, nets, cascades)
    
    ### implement placement
    tile_field = _place_cascades(instances, nets, cascades)
    
    return (tile_field, cascades)
    
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

    
def _add_feedthroughs(instances, nets, cascades):
    '''
        Sometimes, outputs of one cascade are not used in the next cascade, but rather in some subsequent one.
        These postponed ports get a feedthrough for each.
        Feedthrough is an instance of special component which "reserves" position for the postponed port
        in the next cascades until it is finally connected to its destination port.
    '''
    nCascades = len(cascades)
    thru_name_counter = 0
    ft_name_counter = 0
    for ind in range(nCascades-1): # need to traverse pairs (ind, ind+1)
        # select ports from this pair of cascades
        # output ports from previous
        # input ports from next (assuming combinational circuit)
        prev_cascade = cascades[ind]
        next_cascade = cascades[ind+1]
        output_ports = []
        input_ports = []
        for left_inst_name in prev_cascade:
            ports = instances[left_inst_name].get_output_port_names()
            output_ports += [(left_inst_name, port) for port in ports]
        for right_inst_name in next_cascade:
            ports = instances[right_inst_name].get_input_port_names()
            input_ports += [right_inst_name+'.'+port for port in ports]
        
        # exclude ports which are endpoints of nets that connect these two cascades
        # leave only ports (should be outputs) which are not connected to the next cascade, but rather are postponed
        postponed_ports = []
        for left_port in output_ports:
            net_name, other_port = _netlist_operations_find_net_and_other_port(nets, left_port)
            port_str = other_port[0] + '.' + other_port[1]
            if (port_str not in input_ports): # TODO is 'tuple in list' allowed?
                postponed_ports.append((left_port, other_port, net_name))
        #print 'POSTPONED PORTS FOR CASCADES', ind, 'AND', ind+1, ':'
        #print postponed_ports
        
        # for each postponed port, add a feedthrough to the 'next_cascade' 
        # and split its net in two
        for pp in postponed_ports:
            left_port = pp[0]
            other_port = pp[1]
            net_name = pp[2]
            
            # create and register a feedthrough
            thru_name = 'THRU' + str(thru_name_counter)
            thru_name_counter += 1
            thru = wires.FEEDTHROUGH(thru_name)
            instances[thru_name] = thru
            next_cascade.append(thru_name)
            
            # split net
            del nets[net_name]
            
            seg0_name = net_name + '_FT' + str(ft_name_counter)
            ft_name_counter += 1
            nets[seg0_name] = [left_port, (thru_name, 'Input')]
            
            seg1_name = net_name + '_FT' + str(ft_name_counter)
            ft_name_counter += 1
            nets[seg1_name] = [(thru_name, 'Output'), other_port]
            
    
def _netlist_operations_find_net_and_other_port(nets, port):
    for net_name in nets:
        net = nets[net_name]
        if (len(net) != 2):
            raise RuntimeError('Expected a net to be 2-terminal: ' + net_name)
        if (net[0][0] == port[0] and net[0][1] == port[1]):
            return (net_name, net[1])
        elif (net[1][0] == port[0] and net[1][1] == port[1]):
            return (net_name, net[0])
    # if got here, then no net was found
    raise RuntimeError('Cannot find net with port ' + str(port))
    
def _netlist_operations_find_net(nets, port):
    for net_name in nets:
        net = nets[net_name]
        if (len(net) != 2):
            raise RuntimeError('Expected a net to be 2-terminal: ' + net_name)
        if (net[0][0] == port[0] and net[0][1] == port[1]):
            return (net_name, net)
        elif (net[1][0] == port[0] and net[1][1] == port[1]):
            return (net_name, net)
    # if got here, then no net was found
    raise RuntimeError('Cannot find net with port ' + str(port))
    
    
def _netlist_operations_find_the_other_port(nets, port):
    '''
        Returns a port to which given port is connected.
    '''
    for net_name in nets:
        net = nets[net_name]
        if (len(net) != 2):
            raise RuntimeError('Expected a net to be 2-terminal: ' + net_name)
        if (net[0][0] == port[0] and net[0][1] == port[1]):
            return net[1]
        elif (net[1][0] == port[0] and net[1][1] == port[1]):
            return net[0]
    # if got here, then no net was found
    raise RuntimeError('Cannot find net with port ' + str(port))


import random
def _find_optimal_intracascade_ordering(instances, nets, cascades):
    print 'WARNING: Randomly shuffling components within cascades'
    for cascade in cascades:
        random.shuffle(cascade)

            
def _add_crossings(instances, nets, cascades):
    '''
        Adds wire crossings in inter-cascade space.
        After the optimal intra-cascade ordering was determined, any leftover
        wire crossings are dealt with in this routine.
    '''
    # these number are appended to names of crossings and feedthroughs used along with crossings
    cross_name_cnt = 0
    cross_ft_name_cnt = 0
    # iterate over cascade pairs (including freshly inserted cascades)
    idx = 0
    while idx < len(cascades)-1: # len(cascades) may increase in process
        # extract output ports from left cascade and input ports from right cascade.
        # ports must be sorted by their vertical position from top to bottom (relative position by now,
        # since absolute position will not be known until placement implementation)
        prev_cascade = cascades[idx]
        next_cascade = cascades[idx+1]
        left_ports = []
        right_ports_pos = {} # mapping {port -> order number from top}
        for left_inst_name in prev_cascade:
            ports = instances[left_inst_name].get_output_port_names_sorted()
            left_ports += [(left_inst_name, port) for port in ports]
        pos = 0
        for right_inst_name in next_cascade:
            ports = instances[right_inst_name].get_input_port_names_sorted()
            for port in ports:
                right_ports_pos[(right_inst_name, port)] = pos
                pos += 1
            
        # determine presence of any crossings between this pair of cascades.
        crossings_exist = False
        for i in range(len(left_ports) - 1):
            # it is sufficient to check whether any two currently neighboring nets cross.
            left_port_1 = left_ports[i]     
            left_port_2 = left_ports[i+1]   
            right_port_1 = _netlist_operations_find_the_other_port(nets, left_port_1)
            right_port_2 = _netlist_operations_find_the_other_port(nets, left_port_2)
            right_port_1_pos = right_ports_pos[right_port_1]
            right_port_2_pos = right_ports_pos[right_port_2]
            if (right_port_1_pos > right_port_2_pos): # if port_1 is below port_2
                crossings_exist = True
                break
        
        #print 'CASCADES', idx, 'AND', idx+1, '- CROSSINGS EXIST:', crossings_exist
        
        # insert crossings
        if (crossings_exist):
            i = 0
            new_cascade = []
            while i < len(left_ports):
                left_port_1 = left_ports[i]     
                net_name_1, right_port_1 = _netlist_operations_find_net_and_other_port(nets, left_port_1)
                right_port_1_pos = right_ports_pos[right_port_1]
                
                there_is_bottom_port = False
                if ((i+1) < len(left_ports)):
                    left_port_2 = left_ports[i+1]   
                    net_name_2, right_port_2 = _netlist_operations_find_net_and_other_port(nets, left_port_2)
                    right_port_2_pos = right_ports_pos[right_port_2]
                    there_is_bottom_port = True
                
                if (there_is_bottom_port and right_port_1_pos > right_port_2_pos): # if nets cross
                    # create new crossings instance
                    cr_name = 'CROSS_' + str(cross_name_cnt)
                    cross_name_cnt += 1
                    cr = wires.DIRECTED_BICHANNEL_CROSSING(cr_name)
                    instances[cr_name] = cr
                    new_cascade.append(cr_name)
                    
                    # split and create new nets
                    del nets[net_name_1]
                    nets[net_name_1 + '_CR0'] = [left_port_1, (cr_name, 'InputA')]
                    nets[net_name_1 + '_CR1'] = [(cr_name, 'OutputA'), right_port_1]
                    del nets[net_name_2]
                    nets[net_name_2 + '_CR0'] = [left_port_2, (cr_name, 'InputB')]
                    nets[net_name_2 + '_CR1'] = [(cr_name, 'OutputB'), right_port_2]
                    
                    # skip port below
                    i += 1
                else: # if nets do not cross or if left_port_1 is the bottom port
                    # create new FEEDTHROUGH for net containing left_port_1
                    ft_name = 'CROSS_FT_' + str(cross_ft_name_cnt)
                    cross_ft_name_cnt += 1
                    ft = wires.FEEDTHROUGH(ft_name)
                    instances[ft_name] = ft
                    new_cascade.append(ft_name)
                    
                    # split and create new nets
                    del nets[net_name_1]
                    nets[net_name_1 + '_CRFT0'] = [left_port_1, (ft_name, 'Input')]
                    nets[net_name_1 + '_CRFT1'] = [(ft_name, 'Output'), right_port_1]
                    
                i += 1
            
            # insert freshly created cascade with crossings between two current cascades
            cascades.insert(idx+1, new_cascade)
            
        idx += 1
            

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
    for cascade in cascades:
        for inst_name in cascade:
            inst = instances[inst_name]

            row = offset_row
            col = offset_col
            
            tile_field.place_component(row = row, col = col, component = inst)
            inst.set_pos_in_tiles(row = row, col = col)
            
            offset_row += 9
            
        offset_col += 9
        offset_row = 9
    
    
    return tile_field
    