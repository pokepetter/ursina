from ursina import *


class RadialMenu(Entity):
    def __init__(self, buttons=list(), **kwargs):
        super().__init__()
        self.parent = camera.ui
        self.buttons = buttons
        origin = Entity(parent=self)
        self.open_at_cursor = True
        self.open_duration = .25

        self.bg = Panel(parent=self, model='quad', z=99, scale=999, collider='box', color=color.color(0,0,0,.1), enabled=False)
        self.z = -99

        offset = lerp(.5, 2, len(self.buttons)/8)
        for i, b in enumerate(self.buttons):
            b.parent = origin
            b.y = offset
            origin.rotation_z = i/len(self.buttons) * 360
            b.world_parent = self
            b.rotation_z = 0
            if hasattr(b, 'text_entity') and b.text_entity:
                b.text_entity.world_scale /= .075

        destroy(origin)
        self.scale = .075

        for key, value in kwargs.items():
            setattr(self, key, value)



    def on_enable(self):
        if not hasattr(self, 'bg'):
            return

        self.bg.enabled = True
        if self.open_at_cursor:
            self.position = mouse.position

        delay_step = self.open_duration / (len(self.children)-1)
        original_scales = [c.scale for c in self.children]
        for i, c in enumerate(self.children):
            if c is self.bg:
                continue

            c.scale = 0
            c.animate_scale(original_scales[i], duration=.2, delay=i*delay_step, curve=curve.out_bounce)


    def input(self, key):
        if key == 'left mouse down' and mouse.hovered_entity in [c for c in self.children if isinstance(c, Button)]:
            invoke(setattr, self, 'enabled', False, delay=.1)
        elif key == 'left mouse down' and mouse.hovered_entity == self.bg:
            invoke(setattr, self, 'enabled', False, delay=.1)


class RadialMenuButton(Button):
    def __init__(self, **kwargs):
        super().__init__(model='sphere', scale=1.3, highlight_scale=1.2, pressed_color=color.azure)


        for key, value in kwargs.items():
            setattr(self, key, value)



if __name__ == '__main__':
    app = Ursina()

    rm = RadialMenu(
        buttons = (
            RadialMenuButton(text='1'),
            RadialMenuButton(text='2'),
            RadialMenuButton(text='3'),
            RadialMenuButton(text='4'),
            RadialMenuButton(text='5', scale=.5),
            RadialMenuButton(text='6', color=color.red),
            ),
        enabled = False
        )
    RadialMenuButton(text='6', color=color.red,x =-.5, scale=.06),
    def enable_radial_menu():
        rm.enabled = True
    cube = Button(parent=scene, model='cube', color=color.orange, highlight_color=color.azure, on_click=enable_radial_menu)
    EditorCamera()
    app.run()
