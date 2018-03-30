from pandaeditor import *


class Tooltip(Entity):

    def __init__(self, text=''):
        super().__init__()

        self.parent = camera.ui
        self.scale *= .1
        self.original_origin = (-.5, -.5)
        self.min_width = 0
        self.min_height = 0
        self.max_width = 0
        self.z = -1

        self.text = Text('''description''')
        if text:
            self.text.text = text
        self.text.align = 'left'
        self.text.parent = self

        self.background = Entity(
            parent = self,
            model = 'quad',
            color = color.black66,
            z = .1,
            )

        self.fit_to_text()


    def fit_to_text(self):
        print('fit')

        # additional scale only accounts for the first line so I can have a title
        additional_scale = 0
        if self.text.raw_text.startswith('<scale:'):
            additional_scale = (
                self.text.scale[1]
                * (float(self.text.raw_text.split('<scale:')[1].split('>')[0]) - 1)
                )

        self.background.scale_x = max(self.min_width, self.text.width + additional_scale)
        self.background.scale_y = max(self.min_height, (self.text.height + additional_scale))
        print(self.text.width, self.background.scale_x)

        #center
        self.background.x = self.background.scale_x / 2
        self.background.y = self.background.scale_y / 2
        self.background_scale_without_margin = self.background.scale
        self.text.y = self.text.height - .2
        self.margin = (.5, .5)
        # self.margin = (0,0)
        self.scale = (0,0,0)


    @property
    def margin(self):
        return self._margin

    @margin.setter
    def margin(self, value):
        # print('set margin to:', value)
        self._margin = value
        self.background.scale_x = self.background_scale_without_margin[0] + value[0]
        self.background.scale_y = self.background_scale_without_margin[1] + value[1]
        self.origin = (self.original_origin[0]- value[0], self.original_origin[0] - value[1])

    @property
    def margin_x(self):
        return self._margin[0]

    @margin_x.setter
    def margin_x(self, value):
        self.margin = (value, self.margin[1])

    @property
    def margin_y(self):
        return self._margin[1]

    @margin_y.setter
    def margin_y(self, value):
        self.margin = (self.margin[0], value)

    @property
    def max_width(self):
        return self._max_width

    @max_width.setter
    def max_width(self, value):
        self._max_width = value
        if value == 0:
            return

        self.text.wordwrap = value
        self.fit_to_text()


    def update(self, dt):
        self.position = (
            (mouse.x * camera.aspect_ratio) + (self.margin_x * .05) + .01,
            mouse.y + (self.margin_y * .05) + .01
            )
        self.x = min(self.x, (.5 * window.aspect_ratio) - (self.background.scale_x * .1))
        self.y = min(self.y, .5 - (self.background.scale_y * .1))


if __name__ == '__main__':
    app = PandaEditor()

    tooltip_test = Tooltip(
    '<scale:1.5>' + 'Rainstorm' + '<scale:1> \n\n' +
'''Summon a <blue>rain
storm <default>to deal 5 <blue>water
damage <default>to <red>everyone, <default>including <orange>yourself. <default>
Lasts for 4 rounds.'''.replace('\n', ' '))

    # tooltip_test.text.line_height = .75
    tooltip_test.max_width = 40
    tooltip_test.enabled = True
    tooltip_test.animate_scale(Vec3(.1, .1, 1))
    # origin = Entity(model='quad', color=color.red, scale=(.1,.1), parent=tooltip_test, position=(0,0))
    app.run()
