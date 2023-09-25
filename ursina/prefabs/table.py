""" """
from ursina import Entity, Text, Keys
from ursina import color, camera, mouse, floor, destroy


class Table(Entity):
    default_color = color.black66
    highlight_color = color.blue

    def __init__(self, row_height: float, col_widths: list[float], border: float = .001, max_lines: int = 10, **kwargs):
        """ Generates a Table layout.

        :param row_height: the height for each row
        :param col_widths: contains the width for each column. Also defined the amount of cols
        :param border: (default: 0.001) border around the cells
        :param max_lines: determines how many lines should be displayed
        """
        super().__init__(parent=camera.ui)

        self._row_height = row_height
        self._col_widths = col_widths
        self._border = border
        self._max_lines = max_lines

        self._scroll = 0
        self.scroll = 0
        self._rows: list(tuple(Entity, Text)) = []
        self._selected_row_idx = -1

        self._table_width = sum(self._col_widths) + len(self._col_widths) * self._border + self._border
        self._table_height = self._max_lines * (self._row_height + self._border) + self._border
        self.bg = Entity(parent=self, model='quad', origin=(-.5, .5), scale=(self._table_width, self._table_height),
                         color=color.white,
                         collider='box')

        self.scroll_parent = Entity(parent=self)

        for key, value in kwargs.items():
            setattr(self, key, value)

    def input(self, key: Keys):
        """ user input handling

        :param key: ursina.Keys
        """
        if self.bg.hovered:
            if key == 'scroll down':
                if self.scroll + self._max_lines < len(self.scroll_parent.children):
                    self.scroll += 1
            elif key == 'scroll up':
                if self.scroll > 0:
                    self.scroll -= 1

            if key == 'left mouse down':
                y = floor(-mouse.point.y * self._max_lines)
                self.select_row(y + self._scroll)

    def deselect_row(self, row_idx: int):
        """ deselects the current selected row which is marked. Changes the color back to the default color.

        :param row_idx: index for the row to deselect
        """
        if row_idx >= 0:
            for ele, _ in self._rows[row_idx]:
                ele.color = self.default_color

    def select_row(self, row_idx: int):
        """ selects and marks a row as the new selected row.
        Also calls the deselect_row method with the prev selected row.

        :param row_idx: index for the row to select
        """
        self.deselect_row(self._selected_row_idx)
        for ele, _ in self._rows[row_idx]:
            ele.color = self.highlight_color
        self._selected_row_idx = row_idx

    def fill(self, data: list[list]):
        """Destroys the previous elements (if exist) and refills the table with the given data.

        :param data: content to fill the table. The matrix must be a 2D array [row][col_entries].
        """
        for ele, txt in self._rows:
            destroy(ele)
            destroy(txt)
        self._rows = []

        for row_idx in range(0, len(data)):
            pos_y = - row_idx * (self._row_height + self._border) - self._border
            row_parent = Entity(parent=self.scroll_parent)
            cols = []

            for col_idx in range(0, len(self._col_widths)):
                pos_x = sum(self._col_widths[:col_idx]) + col_idx * self._border + self._border
                try:
                    box_text = data[row_idx][col_idx]
                except IndexError as _:
                    print("Error: Table - data invalid", data)
                    box_text = ""

                ele = Entity(parent=row_parent, origin=(-.5, .5), model='quad', color=self.default_color,
                             scale=(self._col_widths[col_idx], self._row_height), x=pos_x, y=pos_y, z=-.1)
                txt = Text(parent=row_parent, origin=(-.5, .5), text=box_text,
                           x=pos_x, y=pos_y, z=-.2)
                cols.append((ele, txt))
            self._rows.append(cols)

        self.scroll = 0

    @property
    def scroll(self) -> int:
        """ gets the current scroll value """
        return self._scroll

    @scroll.setter
    def scroll(self, value: int):
        """ scrolls the level overview panel

        :param value: scroll value to move the panel overview up or down
        """
        self._scroll = value
        for idx, child in enumerate(self.scroll_parent.children):
            if idx < value or idx > value + self._max_lines - 1:
                child.enabled = False
            else:
                child.enabled = True

        self.scroll_parent.y = value * (self._row_height + self._border)


if __name__ == '__main__':
    """ generate a simple table for a lobby menu """
    import random
    from ursina import Ursina

    app = Ursina()

    # fill the table with [game_name, player_count, map_name, ping]
    game_data = []
    for i in range(0, 20):
        game_data.append([f'game name {i}',
                          f'{random.randint(0, 5)} / 5',
                          'A new trial',
                          random.randint(10, 100)
                          ]
                         )

    lobby_bg = Entity(parent=camera.ui, position=(-.4, .4))
    table = Table(max_lines=10, row_height=.03, col_widths=[.15, .1, .2, .1], parent=lobby_bg)
    table.fill(game_data)

    app.run()
