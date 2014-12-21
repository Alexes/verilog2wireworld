'''
    EDIF2WW project file.
    Contains WireWorld LPM cells for the Tile algorithm of size 6.
    Gates are communicated in the format:
    SPACE   empty
    H       electron head
    T       electron tail
    C       conductor
'''

class LPM_AND:
    _pattern = [
        '                  ',
        '                  ',
        'CCCCCCCC          ',
        '        CCC       ',
        '     C C   C      ',
        '    CCC    C      ',
        '   C C C C C      ',
        '   C    CCC  C   C',
        '    C    C CC C C ',
        'CCC C         C C ',
        '   C           C  ',
        '                  '
    ]
    def get_pattern(self):
        return self._pattern
    def get_delay(self):
        return 24
    def get_tile_size(self):
        return (3, 2)
    def get_cell_size(self):
        return (18, 12)
    def get_port_local_pos(self, port):
        ''' Ports location is given in WW cell coordinate space inside gate pattern '''
        if (port == 'Data0x0'):
            return (0, 2)
        elif (port == 'Data1x0'):
            return (0, 9)
        elif (port == 'Result0'):
            return (17, 7)
        
        
def instantiate_LPM_AND(size, width):
    if (size != 2 or width != 1):
        raise Error('Currently LPM_AND supports only LPM_SIZE=2 and LPM_WIDTH=1')
    return LPM_AND()
    
