"""
ursina/array_tools.py

This module provides utility functions and classes for working with arrays and lists,
including flattening, enumerating, and manipulating 2D and 3D arrays. It also includes
functions for sampling and rotating 2D lists, as well as converting between strings and 2D lists.
"""

def flatten_list(target_list):
    """
    Flatten a list of lists into a single list.

    Args:
        target_list (list): The list of lists to flatten.

    Returns:
        list: A single flattened list.
    """
    import itertools
    return list(itertools.chain(*target_list))


def flatten_completely(target_list):
    """
    Flatten a nested list completely into a single list.

    Args:
        target_list (list): The nested list to flatten.

    Yields:
        element: Each element in the flattened list.
    """
    for i in target_list:
        if isinstance(i, (tuple, list)):
            for j in flatten_list(i):
                yield j
        else:
            yield i


def enumerate_2d(target_2d_list):
    """
    Enumerate a 2D list, yielding the coordinates and value of each element.

    Args:
        target_2d_list (list): The 2D list to enumerate.

    Yields:
        tuple: A tuple containing the coordinates (x, y) and the value.
    """
    for x, line in enumerate(target_2d_list):
        for y, value in enumerate(line):
            yield (x, y), value


def enumerate_3d(target_3d_list):
    """
    Enumerate a 3D list, yielding the coordinates and value of each element.

    Args:
        target_3d_list (list): The 3D list to enumerate.

    Yields:
        tuple: A tuple containing the coordinates (x, y, z) and the value.
    """
    for x, vertical_slice in enumerate(target_3d_list):
        for y, log in enumerate(vertical_slice):
            for z, value in enumerate(log):
                yield (x, y, z), value


from typing import List

class Array2D(list):
    """
    A 2D array class that extends the built-in list.

    Attributes:
        width (int): The width of the array.
        height (int): The height of the array.
        default_value: The default value for elements in the array.
    """
    __slots__ = ('width', 'height', 'default_value')

    def __init__(self, width:int=None, height:int=None, default_value=0, data:List[List]=None):
        """
        Initialize the Array2D.

        Args:
            width (int, optional): The width of the array. Required if no data is provided.
            height (int, optional): The height of the array. Required if no data is provided.
            default_value (optional): The default value for elements in the array. Defaults to 0.
            data (List[List], optional): The data to initialize the array with. If provided, width and height are inferred from the data.

        Raises:
            ValueError: If width and height are not provided when no data is given, or if the data is invalid.
        """
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
        """
        Convert the array to a string representation.

        Returns:
            str: The string representation of the array.
        """
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
        """
        Return a string representation of the array with coordinates.

        Returns:
            str: The string representation of the array with coordinates.
        """
        lines = self.to_string().strip().split('\n')
        longest_number = int(len(str(self.height)))
        for y in range(self.height-1, -1, -1):
            lines[y] = f'{self.height-1-y:<{longest_number}}| {lines[y]}'

        padding = longest_number + 2
        lines.append(f'{"o":<{padding}}{"-"*(self.width)}w:{self.width}')
        result = '\n'+'\n'.join(lines)
        return result

    def map(self, func):
        """
        Apply a function to each element in the array.

        Args:
            func (function): The function to apply. It should take three arguments: x, y, and value.

        Returns:
            Array2D: The modified array.
        """
        for (x, y), value in enumerate_2d(self):
            self[x][y] = func(x, y, value)
        return self

    def reset(self):
        """
        Reset the array to the default value.
        """
        for x in range(self.width):
            for y in range(self.height):
                self[x][y] = self.default_value

    def paste(self, data, x, y, ignore=-1):
        """
        Paste another Array2D into this array at the specified coordinates.

        Args:
            data (Array2D): The data to paste.
            x (int): The x-coordinate to start pasting.
            y (int): The y-coordinate to start pasting.
            ignore (optional): The value to ignore when pasting. Defaults to -1.
        """
        for true_x in range(x, min(self.width, x+data.width)):
            for true_y in range(y, min(self.height, y+data.height)):
                if data[true_x-x][true_y-y] == ignore:
                    continue
                self[true_x][true_y] = data[true_x-x][true_y-y]

    def add_margin(self, top=0, right=0, bottom=0, left=0, value=None):
        """
        Add a margin to the array.

        Args:
            top (int, optional): The number of rows to add to the top. Defaults to 0.
            right (int, optional): The number of columns to add to the right. Defaults to 0.
            bottom (int, optional): The number of rows to add to the bottom. Defaults to 0.
            left (int, optional): The number of columns to add to the left. Defaults to 0.
            value (optional): The value to fill the margin with. Defaults to the array's default value.

        Returns:
            Array2D: The new array with the added margin.

        Raises:
            ValueError: If any of the margin values are negative.
        """
        if top < 0 or right < 0 or right < 0 or left < 0:
            raise ValueError('input must be >= 0')
        if value is None:
            value = self.default_value

        new_width = self.width + right + left
        new_height = self.height + top + bottom
        new_array = Array2D(new_width, new_height, default_value=value)
        new_array.paste(self, left, bottom)
        return new_array

    def get_area(self, start, end, allow_out_of_bounds=False):
        """
        Get a sub-area of the array.

        Args:
            start (tuple): The starting coordinates (x, y) of the sub-area.
            end (tuple): The ending coordinates (x, y) of the sub-area.
            allow_out_of_bounds (bool, optional): Whether to allow out-of-bounds coordinates. Defaults to False.

        Returns:
            Array2D: The sub-area of the array.
        """
        cropped_array = Array2D(width=end[0]-start[0], height=end[1]-start[1], default_value=self.default_value)
        if not allow_out_of_bounds:
            for (x, y), _ in enumerate_2d(cropped_array):
                cropped_array[x][y] = self[x+start[0]][y+start[1]]
        else:
            for (x, y), _ in enumerate_2d(cropped_array):
                try:
                    cropped_array[x][y] = self[x+start[0]][y+start[1]]
                except:
                    cropped_array[x][y] = self.default_value

        return cropped_array

if __name__ == '__main__':
    grid = Array2D(width=16, height=8)
    print(grid)
    padded_grid = grid.add_margin(top=4, right=7, bottom=3, left=2, value=7)
    print('added margin:', padded_grid)
    print('cropped_array:\n', padded_grid.get_area((2,3), (padded_grid.width-7, padded_grid.height-4)))


class Array3D(list):
    """
    A 3D array class that extends the built-in list.

    Attributes:
        width (int): The width of the array.
        height (int): The height of the array.
        depth (int): The depth of the array.
        default_value: The default value for elements in the array.
    """
    __slots__ = ('width', 'height', 'depth', 'default_value', 'data')

    def __init__(self, width:int, height:int, depth:int, default_value=0):
        """
        Initialize the Array3D.

        Args:
            width (int): The width of the array.
            height (int): The height of the array.
            depth (int): The depth of the array.
            default_value (optional): The default value for elements in the array. Defaults to 0.
        """
        self.width = int(width)
        self.height = int(height)
        self.depth = int(depth)
        self.default_value = default_value
        super().__init__([Array2D(self.height, self.depth) for x in range(self.width)])

    def reset(self):
        """
        Reset the array to the default value.
        """
        for x in range(self.width):
            for y in range(self.height):
                for z in range(self.depth):
                    self[x][y][z] = self.default_value


def chunk_list(target_list, chunk_size):
    """
    Yield successive chunks from a list.

    Args:
        target_list (list): The list to chunk.
        chunk_size (int): The size of each chunk.

    Yields:
        list: Each chunk of the list.
    """
    for i in range(0, len(target_list), chunk_size):
        yield target_list[i:i + chunk_size]


def rotate_2d_list(target_2d_list):
    """
    Rotate a 2D list 90 degrees clockwise.

    Args:
        target_2d_list (list): The 2D list to rotate.

    Returns:
        list: The rotated 2D list.
    """
    return [list(row) for row in zip(*target_2d_list[::-1])]  # rotate


def string_to_2d_list(string, char_value_map={'.':0, '#':1}):
    """
    Convert a string representation of a 2D list to an actual 2D list.

    Args:
        string (str): The string representation of the 2D list.
        char_value_map (dict, optional): A mapping of characters to values. Defaults to {'.':0, '#':1}.

    Returns:
        list: The 2D list.
    """
    from textwrap import dedent
    grid = dedent(string).strip()
    grid = grid.split('\n')
    grid = [[char_value_map.get(e, 0) for e in line] for line in grid]
    grid = [list(row) for row in zip(*grid[::-1])]  # rotate
    return grid

if __name__ == '__main__':
    from ursina.ursinastuff import _test

    test_input = '''
        #..#.###..####..#..
        #..#.#..#.###...#..
        #..#.###.....#..#..
        .##..#..#.####..#..
        '''
    expected_result = rotate_2d_list([
        [1,0,0,1, 0, 1,1,1,0, 0, 1,1,1,1, 0, 0,1,0,0],
        [1,0,0,1, 0, 1,0,0,1, 0, 1,1,1,0, 0, 0,1,0,0],
        [1,0,0,1, 0, 1,1,1,0, 0, 0,0,0,1, 0, 0,1,0,0],
        [0,1,1,0, 0, 1,0,0,1, 0, 1,1,1,1, 0, 0,1,0,0],
    ])

    _test(string_to_2d_list, (test_input, ), expected_result=expected_result)


def list_2d_to_string(target_2d_list, characters='.#'):
    """
    Convert a 2D list to a string representation.

    Args:
        target_2d_list (list): The 2D list to convert.
        characters (str, optional): The characters to use for the conversion. Defaults to '.#'.

    Returns:
        str: The string representation of the 2D list.
    """
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

    _test(list_2d_to_string, (list_2d, ), expected_result=expected_result)


def sample_bilinear(target_2d_list:Array2D, x, y, clamp_if_outside=True):
    """
    Sample a value from a 2D list using bilinear interpolation.

    Args:
        target_2d_list (Array2D): The 2D list to sample from.
        x (float): The x-coordinate to sample.
        y (float): The y-coordinate to sample.
        clamp_if_outside (bool, optional): Whether to clamp the coordinates if they are outside the bounds of the list. Defaults to True.

    Returns:
        float: The interpolated value.
    """
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
    _test(sample_bilinear, (list_2d, 0, 0), expected_result=1)
    _test(sample_bilinear, (list_2d, 1, 1), expected_result=0)
    _test(sample_bilinear, (list_2d, .5, .5), expected_result=.75)
    _test(sample_bilinear, (list_2d, .5, .75), expected_result=.625)


class LoopingList(list):
    """
    A list that loops around when indexed out of bounds.
    """
    def __getitem__(self, i):
        return super().__getitem__(i % len(self))
