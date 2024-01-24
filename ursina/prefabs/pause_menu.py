from ursina import *


class PauseMenu(Entity):
    def __init__(self, **kwargs):
        super().__init__(ignore_paused=True, **kwargs)
        self.menu = Entity(parent=camera.ui, enabled=False)
        self.bg = Entity(parent=self.menu, model='quad', color=color.black, alpha=.5, scale=3)
        self.pause_text = Text(parent=self.menu, text='PAUSED', origin=(0,0), scale=2)
        self.lock_mouse_on_resume = False

    def on_destroy(self):
        destroy(self.menu)

    def input(self, key):
        if key == 'escape':
            if not application.paused:
                self.lock_mouse_on_resume = mouse.locked
                mouse.locked = False
            else:
                mouse.locked = self.lock_mouse_on_resume

            application.paused = not application.paused # Pause/unpause the game.
            self.menu.enabled = application.paused     # Also toggle "PAUSED" graphic.



if __name__ == '__main__':
    app = Ursina()

    PauseMenu()

    app.run()
