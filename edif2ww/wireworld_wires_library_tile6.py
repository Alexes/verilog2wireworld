'''
    EDIF2WW project file.
    Contains WireWorld patterns such as wires and crossovers
    for Tile Algorithm of size 6. These patterns are used in routing 
    the nets between LPM and other components.
    
    Patterns are communicated in the format:
    SPACE   empty
    H       electron head
    T       electron tail
    C       conductor
'''

_EW_wire_pattern = [
    '      ',
    '      ',
    '      ',
    'CCCCCC',
    '      ',
    '      '
]

_NS_wire_pattern = [
    '  C   ',
    '  C   ',
    '  C   ',
    '  C   ',
    '  C   ',
    '  C   '
]

_NW_wire_pattern = [
    '   C  ',
    '   C  ',
    '   C  ',
    'CCC   ',
    '      ',
    '      '
]

_NE_wire_pattern = [
    '  C   ',
    '  C   ',
    '  C   ',
    '   CCC',
    '      ',
    '      '
]

_ES_wire_pattern = [
    '      ',
    '      ',
    '   CCC',
    '  C   ',
    '  C   ',
    '  C   '
]

_SW_wire_pattern = [
    '      ',
    '      ',
    'CCC   ',
    '   C  ',
    '   C  ',
    '   C  '
]
    
def get_wire_pattern(dir):
    '''
        Returns a wire pattern for specified direction.
        'dir' is a string containing any of the characters: 'NESW' standing for 4 possible directions (assuming von Neumann neighborhood).
        For example, dir=='EW' means a piece of horizontal wire.
        dir=='NS' means vertical wire.
        dir=='NE' means wire corner connection North and East sides.
    '''
    pattern = None
    
    if (len(dir) != 2):
        raise RuntimeError('Currently placing only 2-ended wire segments')
    
    if   (dir == 'EW' or dir == 'WE'):
        pattern = _EW_wire_pattern
    elif (dir == 'NS' or dir == 'SN'):
        pattern = _NS_wire_pattern
    elif (dir == 'NW' or dir == 'WN'):
        pattern = _NW_wire_pattern
    elif (dir == 'NE' or dir == 'EN'):
        pattern = _NE_wire_pattern
    elif (dir == 'ES' or dir == 'SE'):
        pattern = _ES_wire_pattern
    elif (dir == 'SW' or dir == 'WS'):
        pattern = _SW_wire_pattern
        
    if (pattern == None):
        raise RuntimeError('Wires library. Unsupporeted direction: ' + dir)
    
    return pattern
    
    
class MODULE_PORT:
   
    _instance_name = ''
    _direction = ''
    
    _tile_pos_row = 0   # position of the current instance in tile-space
    _tile_pos_col = 0
    
    def __init__(self, instance_name, direction):
        self._instance_name = instance_name
        self._direction = direction
    
    def set_pos_in_tiles(self, row, col):
        ''' 
            Set position of the instance in tile space.
            The position may be changed any number of times,
            in case of multiple re-placement operations, for example.
        '''
        self._tile_pos_row = row
        self._tile_pos_col = col
    
    def get_pos_in_tiles(self):
        ''' 
            Return position of the instance in tile space.
            Returns tuple (row, col)
        '''
        return (self._tile_pos_row, self._tile_pos_col)
    
    def get_pattern(self):
        return ['CCCCCC','CCCCCC','CCCCCC','CCCCCC','CCCCCC','CCCCCC']
        
    def get_size_in_tiles(self):
        ''' Tiles of size 6. Returns tuple (height, width) '''
        return (1, 1)
        
    def get_size_in_cells(self):
        ''' Returns tuple (height, width) '''
        return (6, 6)
        
    def get_port_local_pos(self, port):
        ''' 
            Ports' locations are given in WW cell coordinate space inside gate pattern. 
            Returns tuple (row, col), 0-based.
        '''
        return (0, 0)
            
    def get_port_local_tile_pos(self, port):
        ''' 
            Ports' locations are given in 6-tiles coordinate space 
            outside of the pattern.
            This method returns not the position of the port inside the pattern,
            but rather a location outside of it to which router
            should bring a wire. This allows gates to designate
            specific directions from which wires may connect to their ports.
        '''
        if (self._direction == 'INPUT'):
            return (0, 0+1)
        elif (self._direction == 'OUTPUT'):
            return (0, 0-1)
        else:
            return (0, 0-1)
            
    def get_name(self):
        return self._instance_name
        
    def get_fan_in_count(self):
        return 1
        