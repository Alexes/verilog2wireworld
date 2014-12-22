'''
    EDIF2WW project file.
    Contains WireWorld LPM cells for the Tile Algorithm of size 6.
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
    
    _LPM_instance_name = ''
    
    _tile_pos_row = 0   # position of the current instance in tile-space
    _tile_pos_col = 0
    
    def __init__(self, instance_name, LPM_SIZE, LPM_WIDTH):
        self._LPM_instance_name = instance_name
        if (LPM_SIZE != 2 or LPM_WIDTH != 1):
            raise RuntimeError('Currently LPM_AND supports only LPM_SIZE=2 and LPM_WIDTH=1')
    
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
        return self._pattern
        
    def get_delay(self):
        ''' ... in WW generations '''
        return 24
        
    def get_size_in_tiles(self):
        ''' ... of size 6 '''
        return (2, 3)
        
    def get_size_in_cells(self):
        return (12, 18)
        
    def get_port_local_pos(self, port):
        ''' Ports' locations are given in WW cell coordinate space inside gate pattern '''
        if (port == 'Data0x0'):
            return (2, 0)
        elif (port == 'Data1x0'):
            return (9, 0)
        elif (port == 'Result0'):
            return (7, 17)
            
    def get_port_local_tile_pos(self, port):
        ''' Ports' locations are given in 6-tiles coordinate space local to pattern '''
        if (port == 'Data0x0'):
            return (0, 0)
        elif (port == 'Data1x0'):
            return (1, 0)
        elif (port == 'Result0'):
            return (1, 2)
            
    def get_name(self):
        return self._LPM_instance_name
        
    
class LPM_OR:
    _pattern = [
        '      ',
        '      ',
        'CCC   ',
        '   C C',
        '  CCC ',
        '   C  ',
        '  C   ',
        ' C    ',
        'C     ',
        '      ',
        '      ',
        '      '
    ]
    
    _LPM_instance_name = ''
    
    _tile_pos_row = 0   # position of the current instance in tile-space
    _tile_pos_col = 0
    
    def __init__(self, instance_name, LPM_SIZE, LPM_WIDTH):
        self._LPM_instance_name = instance_name
        if (LPM_SIZE != 2 or LPM_WIDTH != 1):
            raise RuntimeError('Currently LPM_OR supports only LPM_SIZE=2 and LPM_WIDTH=1')
    
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
        return self._pattern
        
    def get_delay(self):
        ''' ... in WW generations '''
        return 6
        
    def get_size_in_tiles(self):
        ''' Tiles of size 6. Returns tuple (height, width) '''
        return (2, 1)
        
    def get_size_in_cells(self):
        ''' Returns tuple (height, width) '''
        return (12, 6)
        
    def get_port_local_pos(self, port):
        ''' 
            Ports' locations are given in WW cell coordinate space inside gate pattern. 
            Returns tuple (row, col), 0-based.
        '''
        if (port == 'Data0x0'):
            return (2, 0)
        elif (port == 'Data1x0'):
            return (8, 0)
        elif (port == 'Result0'):
            return (3, 5)
            
    def get_port_local_tile_pos(self, port):
        ''' Ports' locations are given in 6-tiles coordinate space local to pattern '''
        if (port == 'Data0x0'):
            return (0, 0)
        elif (port == 'Data1x0'):
            return (1, 0)
        elif (port == 'Result0'):
            return (0, 0)
            
    def get_name(self):
        return self._LPM_instance_name
