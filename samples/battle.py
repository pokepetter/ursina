from pandaeditor import *


class Battle(Entity):

    def __init__(self):

        super().__init__()
        self.skills_parent = Entity()
        self.skills_parent.parent = scene.ui
        # self.skills_parent.origin = (0, -.5)
        self.skills_parent.position= (0, -.45)
        # self.skills_parent.scale_y *= 1.25
        self.skills_parent.scale *= .15
        # self.bg.scale *= 5.5
        # self.bg.color = color.red
        skill_amount = 7
        spacing = .05

        for i in range(skill_amount):
            b = Button()
            b.parent = self.skills_parent
            b.origin = (0, -.5)
            b.x = i * 1.05 - ((skill_amount - 1) * 1.05 /2)
            b.y = spacing
            # b.color = color.white33
            b.color = color.color(i*30, .5, .9)
            b.scale_y *= 1.25
            b.add_script()

        bg = Panel()
        bg.parent = self.skills_parent
        bg.origin = (0, -.5)
        bg.position = (0, 0, .1)
        bg.scale_x = skill_amount + ((skill_amount + 1) * spacing)
        bg.scale_y = spacing + b.scale_y + spacing
        # self.skills_parent.add_script('grid_layout')
        # self.skills_parent.grid_layout.spacing = (.05, 0)
        # self.skills_parent.grid_layout.max_x = 10
        # self.skills_parent.grid_layout.update_grid()

    # def fit_inside(self, entities, target):

class SkillButton(Button):
    def __init__(self):
        super().__init__()

    def on_click()


if __name__ == '__main__':
    app = main.PandaEditor()
    s = Battle()
    app.run()
