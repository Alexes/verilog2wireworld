'''
    EDIF2WW project file.
    Extended RLE file writer. This format is supported by Golly
    for storing cellular automata patterns.
'''

'''
    In Extended RLE file, these symbols are used for WireWorld states:
    . empty
    A electron tail
    B electron head
    C copper wire
    
    File should start with dimensions info, which may be left inaccurate
    when opening file from disc with Golly. Dims are only needed when pasting.
    (http://golly.sourceforge.net/Help/formats.html)
    x = width, y = height, rule = rule
'''

def write_rle(filename, pattern):
    '''
        Function accepts CA pattern in a full
        cell-by-cell notation and produces
        Extended RLE file for it.
        
        Input pattern format is such:
        It is a 1D list of strings where
        each char in a string represents a state of a particular cell. 
        States are:
        SPACE   empty
        H       electron head
        T       electron tail
        C       conductor
    '''
    f = open(filename, 'w')
    
    # writing header
    f.write('x = 42, y = 42, rule = WireWorld\n') 
    
    # writing pattern
    for input_line in pattern:
        output_line = ''
        for c in input_line:
            if (c == ' '):
                output_line += '.'
            elif (c == 'H'):
                output_line += 'B'
            elif (c == 'T'):
                output_line += 'A'
            elif (c == 'C'):
                output_line += 'C'
        output_line += '$\n'
        f.write(output_line)
    
    f.close()
    
