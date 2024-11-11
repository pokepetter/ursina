def _test(function, test_input, expected_result):
    result = function(test_input)
    if result == expected_result:
        print('PASSED:', function.__name__)
    else:
        print('FAILED:', function.__name__)
        print('result:', result)
        print('expected result:', expected_result)


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
        flat = flatten_list(self)
        if max(len(str(value)) for value in flatten_list(self)) > 1:    # separate each element with ', '
            for y in range(self.height-1, -1, -1):
                line = ', '.join([str(self[x][y]) for x in range(self.width)])
                lines.append(line)
        else:   # make string without spaces since all the values are the same width
            for y in range(self.height-1, -1, -1):
                line = ''.join([str(self[x][y]) for x in range(self.width)])
                lines.append(line)


        return '\n'.join(lines)

    def __str__(self):
        lines = self.to_string().strip().split('\n')
        longest_number = int(len(str(self.height)))
        for y in range(self.height-1, -1, -1):
            lines[y] = f'{self.height-1-y:<{longest_number}}| {lines[y]}'
        
        padding = longest_number + 2
        lines.append(f'{"o":<{padding}}{"-"*(self.width)}w:{self.width}')
        result = '\n'+'\n'.join(lines)
        return result

                  
    def reset(self):
        for x in range(self.width):
            for y in range(self.height):
                self[x][y] = self.default_value

    def paste(self, data, x, y, ignore=-1):
        for true_x in range(x, min(self.width, x+data.width)):
            for true_y in range(y, min(self.height, y+data.height)):
                if data[true_x-x][true_y-y] == ignore:
                    continue
                self[true_x][true_y] = data[true_x-x][true_y-y]


    def add_margin(self, top=0, right=0, bottom=0, left=0, value=None):
        if top < 0 or right < 0 or right < 0 or left < 0:
            raise ValueError('input must be >= 0')
        if value is None:
            value = self.default_value

        new_width = self.width + right + left
        new_height = self.height + top + bottom
        new_array = Array2D(new_width, new_height, default_value=value)
        new_array.paste(self, left, bottom)
        return new_array
    

    def get_area(self, start, end):
        cropped_array = Array2D(width=end[0]-start[0], height=end[1]-start[1], default_value=self.default_value)
        # print('original_size:', self.width, self.height, 'new_size:', end[0]-start[0], end[1]-start[1])
        for (x, y), _ in enumerate_2d(cropped_array):
            cropped_array[x][y] = self[x+start[0]][y+start[1]]

        return cropped_array

if __name__ == '__main__':
    grid = Array2D(width=16, height=8)
    print(grid)
    padded_grid = grid.add_margin(top=4, right=7, bottom=3, left=2, value=7)
    print('added margin:', padded_grid)
    print('cropped_array:\n', padded_grid.get_area((2,3), (padded_grid.width-7, padded_grid.height-4)))


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

