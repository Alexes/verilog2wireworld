'''
    EDIF2WW project file.
    Contains WireWorld cellular automaton universe implementation.
'''

class WireWorldUniverse:
    _field = []
    _width = 0
    _height = 0
    def __init__(self, width, height):
        for row in range(height):
            self._field.append([' '] * width)
        self._width = width
        self._height = height
    
    def get_width(self):
        return self._width
        
    def get_height(self):
        return self._height
        
    def write_pattern(self, x, y, pattern):
        '''
            Writes given pattern with its
            top-left corner placed at (x, y).
            Origin is the top-left corner of the universe.
            Universe cells at the destination get
            overwritten, so the caller is responsible
            for ensuring to patterns overlap. 
            In future this may change.
            
            'pattern' is a 1D array of strings.
        '''
        pattern_width = len(pattern[0]) # assuming pattern shape is OK
        pattern_height = len(pattern)
        for r in range(pattern_height):
            for c in range(pattern_width):
                self._field[r + x][c + y] = pattern[r][c]
                
    def get_field(self):
        return self._field