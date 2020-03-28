from ursina import *

class ColorMenu(Entity):
    def __init__(self, scene_editor):
        self.scene_editor = scene_editor
        super().__init__(parent=self.scene_editor.ui_parent)

        self.menu = Panel(
            parent=self,
            model='quad',
            origin=(-.5,.5),
            scale=.5,
            collider='box',
            color=color._32,
            enabled=False,
            )


        for i, (key, value) in enumerate(color.colors.items()):
            b = Button(parent=self.menu, scale=.1, z=-.1, color=value)

            def on_click(value=value):
                self.scene_editor.selection.color = value
                print('set color', value)

            b.on_click = on_click

            grid_layout(self.menu.children, max_x=10, offset=(0,0,-.1))



    def input(self, key):
        # open
        if key == 'c' and mouse.hovered_entity in self.scene_editor.entities:
            self.scene_editor.selection = mouse.hovered_entity
            self.open()

        # close
        if not self.menu.enabled:
            return
        if (key == 'escape'
        or key == 'left mouse down' and not mouse.hovered_entity
        or key == 'left mouse down' and mouse.hovered_entity == self.scene_editor.world_plane
        or key == 'left mouse down' and not mouse.hovered_entity == self.menu
        or key == 'right mouse down'
        ):
            self.menu.enabled = False
            print('deactive color menu')


    def open(self):
        self.menu.position = self.scene_editor.selection.screen_position
        invoke(setattr, self.menu, 'enabled', True, delay=.05)



if __name__ == '__main__':
    app = Ursina()
    cube = Entity(model='cube', collider='box')
    scene_editor = Entity(parent=camera.ui)
    scene_editor.entities = [cube, ]
    scene_editor.ui_parent = Entity(parent=camera.ui)
    scene_editor.world_plane = Entity()
    ColorMenu(scene_editor)

    EditorCamera()
    app.run()
