def _test(function, test_input, expected_result):
    result = function(test_input)
    if result == expected_result:
        print('PASSED:', function.__name__)
    else:
        print('FAILED:', function.__name__)
        print('result:', result)
        print('expected result:', expected_result)

from typing import List
class Array2D(list):
    __slots__ = ('width', 'height', 'default_value')

    def __init__(self, width:int=None, height:int=None, default_value=0, data:List[List]=None):    
        self.default_value = default_value

        if data is not None:                # initialize with provided data
            self.width = len(data)
            self.height = len(data[0])
            if self.width == 0 or self.height == 0:
                raise ValueError("width and height must be >= 1.")

            if any(len(row) != self.height for row in data):
                raise ValueError("all rows in the data must have the same length.")
                
            super().__init__(data)
        
        else:   # Initialize with default values 
            if width is None or height is None:
                raise ValueError("width and height must be provided if no data is given.")
            
            self.width = int(width)
            self.height = int(height)
            super().__init__([[self.default_value for _ in range(self.height)] for _ in range(self.width)])

    def to_string(self):
        lines = []
        for y in range(self.height-1, -1, -1):
            line = ', '.join([str(self[x][y]) for x in range(self.width)])
            lines.append(line)
        return '\n'.join(lines)

    def __str__(self):
        lines = self.to_string().strip().split('\n')
        longest_number = int(len(str(self.height)))
        for y in range(self.height-1, -1, -1):
            lines[y] = f'{self.height-1-y:<{longest_number}}| {lines[y]}'
        
        lines.append(f'{'o':<{longest_number}}{'-'*self.width}')
        result = '\n'.join(lines)
        return result

                  
    def reset(self):
        for x in range(self.width):
            for y in range(self.height):
                self[x][y] = self.default_value


if __name__ == '__main__':
    grid = Array2D(width=16, height=8)
    print(grid)



class Array3D(list):
    __slots__ = ('width', 'height', 'depth', 'default_value', 'data')

    def __init__(self, width:int, height:int, depth:int, default_value=0):
        self.width = int(width)
        self.height = int(height)
        self.depth = int(depth)
        self.default_value = default_value
        super().__init__([Array2D(self.height, self.depth) for x in range(self.width)])

    def reset(self):
        for x in range(self.width):
            for y in range(self.height):
                for z in range(self.depth):
                    self[x][y][z] = self.default_value


def chunk_list(target_list, chunk_size):
    # yield successive chunks from list
    for i in range(0, len(target_list), chunk_size):
        yield target_list[i:i + chunk_size]


def flatten_list(target_list):
    import itertools
    return list(itertools.chain(*target_list))


def flatten_completely(target_list):
    for i in target_list:
        if isinstance(i, (tuple, list)):
            for j in flatten_list(i):
                yield j
        else:
            yield i


def enumerate_2d(target_2d_list):    # usage: for (x, y), value in enumerate_2d(my_2d_list)
    for x, line in enumerate(target_2d_list):
        for y, value in enumerate(line):
            yield (x, y), value


def enumerate_3d(target_3d_list):   # usage: for (x, y, z), value in enumerate_3d(my_3d_list)
    for x, vertical_slice in enumerate(target_3d_list):
        for y, log in enumerate(vertical_slice):
            for z, value in enumerate(log):
                yield (x, y, z), value


def rotate_2d_list(target_2d_list):
    return list(zip(*target_2d_list[::-1]))   # rotate


def string_to_2d_list(string, char_value_map={'.':0, '#':1}):
    from textwrap import dedent
    grid = dedent(string).strip()
    grid = grid.split('\n')
    grid = [[char_value_map.get(e, 0) for e in line] for line in grid]
    grid = list(zip(*grid[::-1]))   # rotate
    return grid

if __name__ == '__main__':
    test_input = '''
        #..#.###..####..#..
        #..#.#..#.###...#..
        #..#.###.....#..#..
        .##..#..#.####..#..
        '''
    expected_result = rotate_2d_list([
        (1,0,0,1, 0, 1,1,1,0, 0, 1,1,1,1, 0, 0,1,0,0),
        (1,0,0,1, 0, 1,0,0,1, 0, 1,1,1,0, 0, 0,1,0,0),
        (1,0,0,1, 0, 1,1,1,0, 0, 0,0,0,1, 0, 0,1,0,0),
        (0,1,1,0, 0, 1,0,0,1, 0, 1,1,1,1, 0, 0,1,0,0),
    ])

    _test(string_to_2d_list, test_input, expected_result)


def list_2d_to_string(target_2d_list, characters='.#'):
    return '\n'.join([''.join([characters[e] for e in line]) for line in target_2d_list])

if __name__ == '__main__':
    list_2d = [
        [1,0,0,1, 0, 1,1,1,0, 0, 1,1,1,1, 0, 0,1,0,0],
        [1,0,0,1, 0, 1,0,0,1, 0, 1,1,1,0, 0, 0,1,0,0],
        [1,0,0,1, 0, 1,1,1,0, 0, 0,0,0,1, 0, 0,1,0,0],
        [0,1,1,0, 0, 1,0,0,1, 0, 1,1,1,1, 0, 0,1,0,0],
    ]
    from textwrap import dedent
    expected_result = dedent('''
        #..#.###..####..#..
        #..#.#..#.###...#..
        #..#.###.....#..#..
        .##..#..#.####..#..
        ''').strip()

    _test(list_2d_to_string, list_2d, expected_result)


class LoopingList(list):
    def __getitem__(self, i):
        return super().__getitem__(i % len(self))

