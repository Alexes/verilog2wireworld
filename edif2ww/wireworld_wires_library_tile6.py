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

_horizontal_wire_pattern = [
    '      ',
    '      ',
    '      ',
    'CCCCCC',
    '      ',
    '      '
]

def get_horizontal_wire_pattern():
    return _horizontal_wire_pattern