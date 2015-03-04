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
    
    