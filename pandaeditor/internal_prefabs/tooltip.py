from pandaeditor import *


class Tooltip(Entity):

    def __init__(self, text=''):
        super().__init__()

        self.origin = (-.5, -.5)
        self.min_width = 0
        self.min_height = 0

        self.text = Text('''description''')
        if text:
            self.text.text = text
        self.text.align = 'left'
        self.text.parent = self

        self.background = Entity(
            model = 'quad',
            color = color.black66,
            )

        additional_scale = 0
        if self.text.raw_text.startswith('<scale:'):
            additional_scale = (
                self.text.scale[1]
                * (1 - float(self.text.raw_text.split('<scale:')[1].split('>')[0]))
                )
        print(additional_scale)

        self.background.scale_x = max(self.min_width, self.text.width + additional_scale)
        self.background.scale_y = max(self.min_height, self.text.height + additional_scale)

        #center
        self.background.x += self.background.scale_x / 2
        # some magic numbers to center it vertically
        self.background.y += .0625
        self.background.y -= ((self.background.scale_y-.25) / 2)
        self.background_scale_without_margin = self.background.scale
        self.margin = (.5, .5)


    @property
    def margin(self):
        return self._margin

    @margin.setter
    def margin(self, value):
        # print('set margin to:', value)
        self._margin = value
        self.background.scale_x = self.background_scale_without_margin[0] + value[0]
        self.background.scale_y = self.background_scale_without_margin[1] + value[1]

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




if __name__ == '__main__':
    app = PandaEditor()
    tooltip_test = Tooltip('test tooltip')
    app.run()
