"""
ursina/prefabs/ascii_editor.py

This module provides an ASCII editor using the Ursina engine. It extends the GridEditor
to allow for editing ASCII art with a customizable palette and font. The editor can render
the ASCII art in real-time and supports copying the art to the clipboard.

Dependencies:
- ursina.prefabs.grid_editor
- ursina.color
- ursina.held_keys
- ursina.Text
- pyperclip
"""

from ursina.prefabs.grid_editor import GridEditor
from ursina import color, held_keys, Text
import pyperclip

class ASCIIEditor(GridEditor):
    """
    ASCIIEditor is a class that extends GridEditor to provide an ASCII art editor.

    Attributes:
        text_entity (Text): The Text entity used to display the ASCII art.
    """
    def __init__(self, size=(61,28), palette=(' ', '#', '|', 'A', '/', '\\', 'o', '_', '-', 'i', 'M', '.'), font='VeraMono.ttf', canvas_color=color.black, line_height=1.1, **kwargs):
        """
        Initialize the ASCIIEditor.

        Args:
            size (tuple, optional): The size of the grid. Defaults to (61,28).
            palette (tuple, optional): The palette of characters for the ASCII art. Defaults to (' ', '#', '|', 'A', '/', '\\', 'o', '_', '-', 'i', 'M', '.').
            font (str, optional): The font used for the ASCII art. Defaults to 'VeraMono.ttf'.
            canvas_color (Color, optional): The color of the canvas. Defaults to color.black.
            line_height (float, optional): The line height for the text. Defaults to 1.1.
            **kwargs: Additional keyword arguments for the GridEditor.
        """
        super().__init__(size=size, palette=palette, canvas_color=canvas_color, **kwargs)
        rotated_grid = list(zip(*self.grid[::-1]))
        text = '\n'.join([''.join(reversed(line)) for line in reversed(rotated_grid)])

        self.text_entity = Text(parent=self.parent, text=text, x=-.0, y=.5, line_height=line_height, font=font)

        self.scale = (self.text_entity.width, self.text_entity.height)
        self.canvas.scale = 1
        self.text_entity.world_parent = self
        self.text_entity.position = (0, 1, -.001)

    def render(self):
        """
        Render the ASCII art by updating the text entity with the current grid.
        """
        rotated_grid = list(zip(*self.grid[::-1]))
        self.text_entity.text = '\n'.join([''.join(reversed(line)) for line in reversed(rotated_grid)])


    def input(self, key):
        """
        Handle input events for the ASCII editor.

        Args:
            key (str): The key that was pressed.
        """
        super().input(key)
        if held_keys['control'] and key == 'c':
            print(self.text_entity.text)
            pyperclip.copy(self.text_entity.text)
        #
        # if held_keys['control'] and key == 'v' and pyperclip.paste().count('\n') == (h-1):
        #     t.text = pyperclip.paste()
        #     undo_index += 1
        #     undo_stack = undo_stack[:undo_index]
        #     undo_stack.append(deepcopy(grid))

if __name__ == '__main__':
    from ursina import Ursina
    app = Ursina()

    editor = ASCIIEditor()

    app.run()
