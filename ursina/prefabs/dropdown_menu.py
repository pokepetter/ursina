from ursina import *


class DropdownMenuButton(Button):
    def __init__(self, text='', **kwargs):
        super().__init__(
            scale=(.25,.025),
            origin=(-.5,.5),
            pressed_scale=1,
            text=text,
            **kwargs
            )

        if self.text_entity:
            self.text_entity.x = .05
            self.text_entity.origin = (-.5, 0)
            self.text_entity.scale *= .8


class DropdownMenu(DropdownMenuButton):

    def __init__(self, text='', buttons=list(), **kwargs):
        super().__init__(text=text)
        self.position = window.top_left
        self.buttons = buttons
        for i, b in enumerate(self.buttons):
            b.world_parent = self
            b.original_scale = b.scale
            b.x = 0
            b.y = -i-1 *.98
            b.enabled = False

            if isinstance(b, DropdownMenu):
                for e in b.buttons:
                    e.x = 1
                    e.y += 1

        self.arrow_symbol = Text(world_parent=self, text='>', origin=(.5,.5), position=(.95, 0), color=color.gray)
        for key, value in kwargs.items():
            setattr(self, key, value)


    def open(self):
        for i, b in enumerate(self.buttons):
            invoke(setattr, self.buttons[i], 'enabled', True, delay=(i*.02))

    def close(self):
        for i, b in enumerate(reversed(self.buttons)):
            b.enabled = False


    def on_mouse_enter(self):
        super().on_mouse_enter()
        self.open()

    def input(self, key):
        if key == 'left mouse down' and mouse.hovered_entity and mouse.hovered_entity.has_ancestor(self):
            self.close()

    def update(self):
        if self.hovered or mouse.hovered_entity and mouse.hovered_entity.has_ancestor(self):
            return

        self.close()


if __name__ == '__main__':
    from ursina.prefabs.dropdown_menu import DropdownMenu, DropdownMenuButton

    app = Ursina()
    # DropdownMenu(text='File')
    DropdownMenu('File', buttons=(
        DropdownMenuButton('New'),
        DropdownMenuButton('Open'),
        DropdownMenu('Reopen Project', buttons=(
            DropdownMenuButton('Project 1'),
            DropdownMenuButton('Project 2'),
            )),
        DropdownMenuButton('Save'),
        DropdownMenu('Options', buttons=(
            DropdownMenuButton('Option a'),
            DropdownMenuButton('Option b'),
            )),
        DropdownMenuButton('Exit'),
        ))

    app.run()
