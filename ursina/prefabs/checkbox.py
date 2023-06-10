from ursina import Button, Text, Quad


class CheckBox(Button):
    def __init__(self, start_state=False, **kwargs):
        super().__init__(start_state=start_state, state=start_state, scale=Text.size, model=Quad(radius=.25))

        for key, value in kwargs.items():
            setattr(self, key, value)


    def on_click(self):
        self.state = not self.state


    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value
        print(value)
        self.text = ' x'[int(value)]


if __name__ == '__main__':
    from ursina import Ursina, Slider
    app = Ursina()
    CheckBox(start_value=True)
    Slider(y=-.1)
    app.run()
