from ursina.prefabs.grid_editor import GridEditor
from ursina import color, held_keys, Text, rotate_2d_list
import pyperclip

class ASCIIEditor(GridEditor):
    def __init__(self, size=(61,28), palette=(' ', '#', '|', 'A', '/', '\\', 'o', '_', '-', 'i', 'M', '.'), font=Text.default_monospace_font, canvas_color=color.black, line_height=1.1, **kwargs):
        super().__init__(size=size, palette=palette, canvas_color=canvas_color, **kwargs)
        rotated_grid = rotate_2d_list(self.grid)
        text = '\n'.join([''.join(reversed(line)) for line in reversed(rotated_grid)])

        self.text_entity = Text(parent=self.parent, text=text, x=-.0, y=.5, line_height=line_height, font=font)

        self.scale = (self.text_entity.width, self.text_entity.height)
        self.canvas.scale = 1
        self.text_entity.world_parent = self
        self.text_entity.position = (0, 1, -.001)

    def render(self):
        rotated_grid = rotate_2d_list(self.grid)
        self.text_entity.text = '\n'.join([''.join(reversed(line)) for line in reversed(rotated_grid)])


    def input(self, key):
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
