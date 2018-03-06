from pandaeditor import *


class TextEditor(Entity):

    def __init__(self):

        super().__init__()
        self.text = Text()
        self.text.font = 'Inconsolata-Regular.ttf'
        # self.text.parent = scene.ui
        # self.text.position = (-.4 * 1.7, .4)
        self.text.position = (-.5, .4)
        # self.text.align = 'top_left'
        self.text.scale *= 4
        self.character_width = .5
        self.line_height = 1
        self.real_text = '''
class TextEditor(Entity):

    def __init__(self):

        super().__init__()
        self.text = Text()
        self.text.parent = scene.ui
        # self.text.position = (-.4 * 1.7, .4)
        '''

        self.replacements = {
            'class '   : '<violet>class <default>',
            ' def '     : '<violet> def <default>',
            'self'     : '<orange>self<default>',
            '__init__'  : '<cyan>__init__<default>',
            'Entity'    : '<lime>Entity<default>'
            }

        self.indicator = Entity(
            model = 'circle_16',
            color = color.azure,
            z = -1,
            scale = (.15, .15)
            )
        self.indicator_line = Entity(
            parent = self.indicator,
            model = 'quad',
            color = color.azure,
            origin = (0, -.5, -.1),
            scale = (.5, 1 / self.indicator.scale_y)
            )


# self.indicator.
    def input(self, key):
        # print(key)
        if held_keys['left alt']:
            if key == 'd' or key == 'd hold':
                self.indicator.x += self.character_width
            if key == 'a' or key == 'a hold':
                self.indicator.x -= self.character_width
            if key == 'w' or key == 'w hold':
                self.indicator.y += self.line_height
            if key == 's' or key == 's hold':
                self.indicator.y -= self.line_height
            if key == 'e' or key == 'e hold':
                self.indicator.x += 10 # to end of word
            if key == 'q' or key == 'q hold':
                self.indicator.x -= 10

        if key == 'scroll up':
            camera.y += 1
        if key == 'scroll down':
            camera.y -= 1

        # self.text.text = self.real_text.replace('def', '<violet>def <default>')
        self.text.text = multireplace(self.real_text, self.replacements)



if __name__ == '__main__':
    loadPrcFileData('', 'win-size 256 512')
    app = main.PandaEditor()
    # window.size = (256, 512)
    camera.orthographic = True
    camera.fov = 60
    camera.x = camera.fov * .4
    camera.y = -camera.fov * .25
    window.color = color.color(0, 0, .1)
    # window.fps_counter = False
    s = TextEditor()
    app.run()
