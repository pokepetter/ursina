from pandaeditor import *


class Battle(Entity):

    def __init__(self):

        super().__init__()
        self.skills_parent = Entity()
        self.skills_parent.parent = scene.ui
        # self.skills_parent.origin = (0, -.5)
        self.skills_parent.position= (0, -.5)
        self.skills_parent.scale *= .2
        self.bg = Panel()
        self.bg.parent = self.skills_parent
        self.bg.origin = (0, -.5)
        self.bg.position = (0, 0, .1)
        self.bg.scale = ((4 * 1.05) + 1.1, 1.0)
        # self.bg.scale *= 5.5
        # self.bg.color = color.red


        for i in range(5):
            b = Button()
            b.parent = self.skills_parent
            b.origin = (0, -.5)
            b.x = i * 1.05 - (4 * 1.05 /2)
            b.y = .025
            # b.scale *= .5

        # self.skills_parent.add_script('grid_layout')
        # self.skills_parent.grid_layout.spacing = (.05, 0)
        # self.skills_parent.grid_layout.max_x = 10
        # self.skills_parent.grid_layout.update_grid()

if __name__ == '__main__':
    app = main.PandaEditor()
    s = Battle()
    app.run()
