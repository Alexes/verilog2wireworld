'''
    EDIF2WW project file.
    Contains WireWorld cellular automaton universe implementation.
    
    Also, contains some logic tied with the Tile Algorithm.
    Specifically, it contains the Tile-level abstraction of a WireWorld field
    and necessary transition from it to the CA cell-level which can then be written to RLE.
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
        
    def write_pattern(self, row, col, pattern):
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
                self._field[r + row][c + col] = pattern[r][c]
                
    def get_field(self):
        return self._field
        
        

        
class TileLevelWireWorldUniverse:
    _field = []
    _width = 0
    _height = 0
    def __init__(self, width, height):
        '''
            width, height - in tiles of size 6x6 CA cells.
            Field cell states may be one of:
            SPACE - empty 
            LPM instance name - if it occupies the tile. One instance usually takes up several tiles
            Crossover instance name - usually takes up several tiles as well
            C - conductor
            These, actually, are more like labels, not states.
            For, example, a LPM_AND gate of tile size 6 has dimensions of 2x3 tiles.
            On Tile-level field, it occupies 6 cells; each cell contains
            the instance's name which acts more like a label or a pointer to the instance.
            
            After the placement and routing is done, Tile-level field is converted into
            CA cell field and written to RLE.
        '''
        for row in range(height):
            self._field.append([' '] * width)
        self._width = width
        self._height = height
        
    def get_width(self):
        return self._width
        
    def get_height(self):
        return self._height
        
    def place_component(self, row, col, component):
        ''' 
            Accepts LPM instance objects and crossovers.
            'row' and 'col' are in tile space.
        '''
        comp_size = component.get_size_in_tiles()
        height = comp_size[0]
        width = comp_size[1]
        instance_name = component.get_name()
        for r in range(height):
            for c in range(width):
                if (self._field[r + row][c + col] == ' '):
                    self._field[r + row][c + col] = instance_name
                else:
                    raise RuntimeError('Tile level of abstraction: component overlap detected.')
                    
    def write_cell_level_universe(self, instances_dict):
        '''
            Writes CA cell level WireWorld field.
            Requires a list of instantiated LPM cells and crossovers,
            because it needs access to their patterns and their names.
        '''
        TILE_SIZE = 6
        ww = WireWorldUniverse(self._width * TILE_SIZE, self._height * TILE_SIZE)
        
        written_instances = {} # which have already been written
        # The loop goes in a classic direction and should
        # meet top-left corners first. However, TODO is to
        # make top-left corner have a special label or smth like that.
        for r in range(self._height):
            for c in range(self._width):
                tile = self._field[r][c]
                if (tile == ' '):
                    continue
                if (tile == 'C'):
                    print 'Conductors are not currently supported... but they should be, really'
                    continue
                if (tile not in written_instances):
                    instance = instances_dict[tile]
                    pattern = instance.get_pattern()
                    pos_row = r * TILE_SIZE
                    pos_col = c * TILE_SIZE
                    ww.write_pattern(pos_row, pos_col, pattern)
                    
                    written_instances[tile] = True # the presense is important, not the value
                
        return ww
        