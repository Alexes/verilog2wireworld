'''
    EDIF2WW project file.
    Net splitter divides multiterminal nets into several 2-terminal nets.
'''

import wireworld_wires_library_tile6 as wires

def split_multiterminal_nets(nets, components):
    '''
        Accepts a netlist and returns new netlist with multiterminal nets divided into several constituent 2-terminal nets.
        Uses DIRECTED_JUNCTION instances to do its job.
        Components collection is needed so that this function can add freshly created DIRECTED_JUNCITON instances.
        
        Original 2-terminals nets are copied by reference!
    '''
    new_nets = {}
    for net_name in nets:
        net = nets[net_name]
        term_count = len(net)
        if (term_count == 2):
            new_nets[net_name] = net # a pointer to the original list
        elif (term_count == 3):
            branches = _split_3_terminal_net(net, net_name, components)
            branch_counter = 0
            for branch in branches:
                new_nets[net_name + '_BRANCH' + str(branch_counter)] = branch
                branch_counter += 1
        else:
            print 'Net splitter ERROR: Currently only 2- and 3-terminal nets are supported'
            
    return new_nets
    
def _split_3_terminal_net(net, net_name, components):
    '''
        Returns a list of lists representing nets.
        Adds necessary instances to 'components' dict.
    '''
    # creating a 3-junction instance
    junction_name = net_name + '_JUNC'
    jun = wires.DIRECTED_JUNCTION(junction_name)
    components[junction_name] = jun
    
    # connecting junction to net endpoints
    found_source = False
    nets_to_add = []
    output_index = 0
    for endpoint in net:
        inst_name = endpoint[0]
        inst = components[inst_name]
        port_name = endpoint[1]
        
        if (port_name in inst.get_output_port_names()):
            if (found_source == True):
                raise RuntimeError('Found net with more than one signal source: ' + net_name)
            nets_to_add.append([(inst_name, port_name), (junction_name, 'Input')])
            found_source = True
        else:
            nets_to_add.append([(inst_name, port_name), (junction_name, 'Output' + str(output_index))])
            output_index += 1
    
    return nets_to_add
    
    