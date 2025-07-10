from ursina.scripts.property_generator import generate_properties_for_class

if __name__ == '__main__':
    from ursina.ursinastuff import _test


def flatten_list(target_list):
    import itertools
    return list(itertools.chain(*target_list))


def flatten_completely(target_list):
    for i in target_list:
        if isinstance(i, tuple | list):
            yield from flatten_list(i)
        else:
            yield i


def enumerate_2d(lst):    # usage: for (x, y), value in enumerate_2d(my_2d_list)
    if isinstance(lst, Array2D):
        width = lst.width
        height = lst.height
    else:
        width = len(lst)
        height = len(lst[0])
    for y in range(height):
        for x in range(width):
            yield (x, y), lst[x][y]


def enumerate_3d(target_3d_list):   # usage: for (x, y, z), value in enumerate_3d(my_3d_list)
    for x, vertical_slice in enumerate(target_3d_list):
        for y, log in enumerate(vertical_slice):
            for z, value in enumerate(log):
                yield (x, y, z), value



@generate_properties_for_class()
class Array2D(list):
    __slots__ = ('width', 'height', 'default_value')

    def __init__(self, width:int=None, height:int=None, default_value=0, data:list[list]=None):
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

    @staticmethod
    def from_string(string, convert_to_type=str, starts_lower_left=True):
            string = string.strip()
            if starts_lower_left:
                data = [[convert_to_type(word.strip()) for word in line.split(',') if word] for line in string.split('\n') if line]
                data = [list(row) for row in zip(*data[::-1], strict=True)]  # rotate
                return Array2D(data=data)
            else:
                return Array2D(data=[[word.strip() for word in line.split(',') if word] for line in string.split('\n') if line])

    def to_string(self, separator=', ', always_separate=False):
        lines = []
        longest_width = max(len(str(value)) for (_,_), value in enumerate_2d(self))

        if always_separate or longest_width > 1:    # separate each element with ', '
            for y in range(self.height-1, -1, -1):
                line = separator.join([f'{str(self[x][y]):>{longest_width}}' for x in range(self.width)])
                lines.append(line)
        else:   # make string without spaces since all the values are the same width
            for y in range(self.height-1, -1, -1):
                line = ''.join([str(self[x][y]) for x in range(self.width)])
                lines.append(line)


        return '\n'.join(lines)

    @property
    def size(self):
        from ursina.vec2 import Vec2
        return Vec2(self.width, self.height)

    def rows_getter(self):
        return [[self[x][y] for x in range(self.width)] for y in range(self.height)]

    def columns_getter(self):
        return [[self[x][y] for y in range(self.height)] for x in range(self.width)]

    def __str__(self):
        lines = self.to_string().strip().split('\n')
        longest_number = int(len(str(self.height)))
        for y in range(self.height-1, -1, -1):
            lines[y] = f'{self.height-1-y:<{longest_number}}| {lines[y]}'

        padding = longest_number + 2
        lines.append(f'{"o":<{padding}}{"-"*(self.width)}w:{self.width}')
        result = '\n'+'\n'.join(lines)
        return result


    def map(self, func):
        for (x, y), value in enumerate_2d(self):
            self[x][y] = func(x, y, value)
        return self


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

    @property
    def bounds(self):
        from ursina.ursinamath import Bounds
        from ursina.vec3 import Vec3
        min_x = self.width
        min_y = self.height
        max_x = 0
        max_y = 0

        for (x, y), value in enumerate_2d(self):
            if value:
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)

        return Bounds(start=Vec3(min_x, min_y, 1), end=Vec3(max_x, max_y, 1))

    def get(self, x, y, default=0):
        x, y = int(x), int(y)
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return default
        return self[x][y]


    def set(self, x, y, value):
        x, y = int(x), int(y)
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return
        self[x][y] = value


    def get_area(self, start, end, allow_out_of_bounds=False):
        cropped_array = Array2D(width=end[0]-start[0], height=end[1]-start[1], default_value=self.default_value)
        # print('original_size:', self.width, self.height, 'new_size:', end[0]-start[0], end[1]-start[1])
        if not allow_out_of_bounds:
            for (x, y), _ in enumerate_2d(cropped_array):
                cropped_array[x][y] = self[int(x+start[0])][int(y+start[1])]
        else:
            for (x, y), _ in enumerate_2d(cropped_array):
                cropped_array[x][y] = self.get(x+start[0], y+start[1], default=self.default_value)

        return cropped_array



if __name__ == '__main__':
    from textwrap import dedent, indent
    grid = Array2D(width=16, height=8)
    # print(grid)
    padded_grid = grid.add_margin(top=4, right=7, bottom=3, left=2, value=7)
    # print('added margin:', padded_grid)
    # print('cropped_array:\n', padded_grid.get_area((2,3), (padded_grid.width-7, padded_grid.height-4)))

    _test(
        Array2D(data=[[1,6], [2,7], [3,8], [4,9], [5,10]]).to_string()
        ==
        indent(dedent('''
        6,  7,  8,  9, 10
        1,  2,  3,  4,  5
        ''').strip(), ' ')
    )

    _test(Array2D(data=[[1,6], [2,7], [3,8], [4,9], [5,10]]).rows == [[1,2,3,4,5], [6,7,8,9,10]])

    _test(Array2D.from_string('''
        0,1,0
        2,3,4
        0,1,1
        0,0,0
        ''', int) ==
        Array2D(data=[
        [0,0,2,0],
        [0,1,3,1],
        [0,1,4,0]
        ])
    )


class Array3D(list):
    __slots__ = ('width', 'height', 'depth', 'default_value')

    def __init__(self, width:int=None, height:int=None, depth:int=None, default_value=0, data:list[list]=None):
        self.default_value = default_value

        if data is not None:                # initialize with provided data
            self.width = len(data)
            self.height = len(data[0])
            self.depth = len(data[0][0])
            if self.width == 0 or self.height == 0 or self.depth == 0:
                raise ValueError("width, height, depth must be >= 1.")

            if any(len(row) != self.height for row in data):
                raise ValueError("all rows in the data must have the same length.")

            super().__init__(data)

        else:   # Initialize with default values
            if width is None or height is None or depth is None:
                raise ValueError("width and height and depth must be provided if no data is given.")

            self.width = int(width)
            self.height = int(height)
            self.depth = int(depth)
            super().__init__([[[self.default_value for _ in range(self.depth)] for _ in range(self.height)] for _ in range(self.width)])


    @property
    def size(self):
        from ursina.vec3 import Vec3
        return Vec3(self.width, self.height, self.depth)


    @property
    def bounds(self):
        from ursina.ursinamath import Bounds
        from ursina.vec3 import Vec3
        min_x = self.width
        min_y = self.height
        min_z = self.depth
        max_x = 0
        max_y = 0
        max_z = 0

        for (x, y, z), value in enumerate_3d(self):
            if value:
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                min_z = min(min_z, z)
                max_x = max(max_x, x)
                max_y = max(max_y, y)
                max_z = max(max_z, z)

        return Bounds(start=Vec3(min_x, min_y, min_z), end=Vec3(max_x, max_y, max_z))


    def get(self, x, y, z, default=0):
        x, y, z = int(x), int(y), int(z)
        try:
            return self[x][y][z]
        except:
            return default


    def reset(self):
        for x,y,z, _ in enumerate_3d(self):
            self[x][y][z] = self.default_value


    def paste(self, data, x, y, z, ignore=-1):
        for true_x in range(x, min(self.width, x+data.width)):
            for true_y in range(y, min(self.height, y+data.height)):
                for true_z in range(z, min(self.depth, y+data.depth)):
                    if data[true_x-x][true_y-y][true_z-z] == ignore:
                        continue
                    self[true_x][true_y][true_z] = data[true_x-x][true_y-y][true_z-z]


def chunk_list(target_list, chunk_size):
    # yield successive chunks from list
    for i in range(0, len(target_list), chunk_size):
        yield target_list[i:i + chunk_size]


def rotate_2d_list(target_2d_list):
    return [list(row) for row in zip(*target_2d_list[::-1], strict=True)]  # rotate


def rotate_3d_list(target_3d_list, clockwise=True): # rotates around the y (up) axis where 1 is 90 degrees clockwise
    new_data = Array3D(width=target_3d_list.depth, height=target_3d_list.height, depth=target_3d_list.width)
    print('rotate array3d, clockwise:', clockwise)

    if clockwise:
        for (x, y, z), value in enumerate_3d(target_3d_list):
            new_x = z
            new_z = target_3d_list.width - 1 - x
            new_data[new_x][y][new_z] = value
    else:
        for (x, y, z), value in enumerate_3d(target_3d_list):
            new_x = target_3d_list.depth - 1 - z
            new_z = x
            new_data[new_x][y][new_z] = value

    return new_data


def string_to_2d_list(string, char_value_map=None): # char_value_map default: {'.': 0, '#': 1}
    from textwrap import dedent
    if char_value_map is None:
        char_value_map = {'.': 0, '#': 1}
    grid = dedent(string).strip()
    grid = grid.split('\n')
    grid = [[char_value_map.get(e, 0) for e in line] for line in grid]
    grid = [list(row) for row in zip(*grid[::-1], strict=True)]  # rotate
    return grid

if __name__ == '__main__':
    from ursina.ursinastuff import _test

    _test(string_to_2d_list('''\
        #..#.###..####..#..
        #..#.#..#.###...#..
        #..#.###.....#..#..
        .##..#..#.####..#..
        ''')
        ==
        rotate_2d_list([
        [1,0,0,1, 0, 1,1,1,0, 0, 1,1,1,1, 0, 0,1,0,0],
        [1,0,0,1, 0, 1,0,0,1, 0, 1,1,1,0, 0, 0,1,0,0],
        [1,0,0,1, 0, 1,1,1,0, 0, 0,0,0,1, 0, 0,1,0,0],
        [0,1,1,0, 0, 1,0,0,1, 0, 1,1,1,1, 0, 0,1,0,0],
    ])
    )


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

    _test(list_2d_to_string(list_2d) == expected_result)


def sample_bilinear(target_2d_list:Array2D, x, y, clamp_if_outside=True):
    X = clamp(int(x), 0, target_2d_list.width-1)
    Y = clamp(int(y), 0, target_2d_list.height-1)
    next_x = clamp(X+1, 0, target_2d_list.width-1)
    next_y = clamp(Y+1, 0, target_2d_list.height-1)

    height_bottom_left = target_2d_list[X][Y]
    height_bottom_right = target_2d_list[next_x][Y]
    height_top_left = target_2d_list[X][next_y]
    height_top_right = target_2d_list[next_x][next_y]

    x_fraction = x - X
    y_fraction = y - Y

    bottom_row_interpolation = (1 - x_fraction) * height_bottom_left + x_fraction * height_bottom_right
    top_row_interpolation = (1 - x_fraction) * height_top_left + x_fraction * height_top_right
    interpolated_height = (1 - y_fraction) * bottom_row_interpolation + y_fraction * top_row_interpolation

    return interpolated_height

if __name__ == '__main__':
    list_2d = Array2D(data=[
        [1,1,0],
        [1,0,0],
        [1,0,0],
    ])
    _test(sample_bilinear(list_2d, 0, 0) == 1)
    _test(sample_bilinear(list_2d, 1, 1) == 0)
    _test(sample_bilinear(list_2d, .5, .5) == .75)
    _test(sample_bilinear(list_2d, .5, .75) == 0.625)



class LoopingList(list):
    def __getitem__(self, i):
        return super().__getitem__(i % len(self))

