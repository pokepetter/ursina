from ursina import Entity, Text, camera, Button, color, mouse, Sequence, Vec3
from math import floor

# Header Comment:
# This file defines the ButtonList class, which is used to create a list of buttons in the Ursina engine.
# The ButtonList class allows for the creation of a list of buttons with customizable properties such as button height, width, colors, and fonts.
# It also provides functionality for handling button clicks and highlighting the selected button.
# Dependencies: Ursina engine, math module

class ButtonList(Entity):
    """
    ButtonList class creates a list of buttons in the Ursina engine.

    Attributes:
        button_dict (dict): Dictionary of button labels and their corresponding actions.
        button_height (float): Height of each button.
        width (float): Width of the button list.
        popup (bool): Whether the button list is a popup.
        color (color): Background color of the button list.
        highlight_color (color): Color of the highlighted button.
        selected_color (color): Color of the selected button.
        font (str): Font used for the button labels.
        clear_selected_on_enable (bool): Whether to clear the selected button when the button list is enabled.
    """
    def __init__(self, button_dict, button_height=1.1, width=.5, popup=False, color=Button.default_color, highlight_color=color.white33, selected_color=color.azure, font=Text.default_font, clear_selected_on_enable=True, **kwargs):
        """
        Initialize the ButtonList.

        Args:
            button_dict (dict): Dictionary of button labels and their corresponding actions.
            button_height (float): Height of each button.
            width (float): Width of the button list.
            popup (bool): Whether the button list is a popup.
            color (color): Background color of the button list.
            highlight_color (color): Color of the highlighted button.
            selected_color (color): Color of the selected button.
            font (str): Font used for the button labels.
            clear_selected_on_enable (bool): Whether to clear the selected button when the button list is enabled.
            **kwargs: Additional keyword arguments.
        """
        self.clear_selected_on_enable = clear_selected_on_enable
        self.button_height = button_height
        self.width = width
        super().__init__(parent=camera.ui, position=(-(width/2), .45))

        self.text_entity = Text(parent=self, font=font, origin=(-.5,.5), text='empty', world_scale=20, z=-.1, x=.01, y=-(button_height*.25*Text.size), line_height=button_height)
        self.bg = Entity(parent=self, model='quad', origin=(-.5,.5), scale=width, color=color, collider='box')
        self.highlight = Entity(parent=self.bg, model='quad', color=highlight_color, scale=(1,self.button_height), origin=(-.5,.5), z=-.01, add_to_scene_entities=False)
        self.selection_marker = Entity(parent=self.bg, model='quad', color=selected_color, scale=(1,self.button_height), origin=(-.5,.5), z=-.02, enabled=False, add_to_scene_entities=False)
        self.button_dict = button_dict

        self.popup = popup
        if self.popup:
            self.close_button = Entity(parent=self, scale=Vec3(100,100,.1), model='quad', collider='box', visible_self=False, on_click=self.disable)

        for key, value in kwargs.items():
            setattr(self, key, value)


    @property
    def button_dict(self):
        """
        Get the button dictionary.

        Returns:
            dict: Dictionary of button labels and their corresponding actions.
        """
        return self._button_dict

    @button_dict.setter
    def button_dict(self, value):
        """
        Set the button dictionary.

        Args:
            value (dict): Dictionary of button labels and their corresponding actions.
        """
        self._button_dict = value
        self.actions = list(self._button_dict.values())
        self.bg.scale_y = self.button_height * len(value) * Text.size
        self.bg.model = 'quad'
        self.bg.origin = self.bg.origin

        self.text_entity.text = '\n'.join(self.button_dict.keys())
        self.text_entity.line_height = self.button_height
        if len(value) > 0:
            self.highlight.scale_y = 1 / len(value)
            self.selection_marker.scale_y = 1 / len(value)


    def input(self, key):
        """
        Handle input events.

        Args:
            key (str): The key that was pressed.
        """
        if key == 'left mouse down' and self.bg.hovered:
            y = floor(-mouse.point.y * len(self.button_dict))
            y = min(y, len(self.button_dict)-1)

            action = self.actions[y]
            self.selection_marker.enabled = True
            self.selection_marker.y = self.highlight.y

            if callable(action):
                action()

            if self.popup:
                self.disable()

        if key == 'left mouse down' and not self.bg.hovered:
            self.selection_marker.enabled = False


    def update(self):
        """
        Update the button list.
        """
        self.highlight.enabled = mouse.hovered_entity == self.bg
        if mouse.hovered_entity == self.bg:
            y = floor(-mouse.point.y * len(self.button_dict))
            y = min(y, len(self.button_dict)-1)
            self.highlight.y = -y / len(self.button_dict)


    def on_disable(self):
        """
        Handle the button list being disabled.
        """
        self.selection_marker.enabled = False

    def on_enable(self):
        """
        Handle the button list being enabled.
        """
        if self.clear_selected_on_enable:
            self.selected = None


    @property
    def selected(self):
        """
        Get the selected button.

        Returns:
            str: The label of the selected button.
        """
        return getattr(self, '_selected', None)
    @selected.setter
    def selected(self, value):
        """
        Set the selected button.

        Args:
            value (str): The label of the button to select.
        """
        self._selected = value
        if not hasattr(self, 'selection_marker'):
            return

        if not value:
            self.selection_marker.enabled = False
            return

        self.selection_marker.enabled = True
        y = list(self.button_dict.keys()).index(value)
        self.selection_marker.y = -y / len(self.button_dict)


if __name__ == '__main__':
    from ursina import Ursina, Func
    app = Ursina()

    default = Func(print, 'not yet implemented')

    def test(a=1, b=2):
        print('------:', a, b)

    button_dict = {}
    for i in range(6, 20):
        button_dict[f'button {i}'] = Func(print, i)

    bl = ButtonList(button_dict, font='VeraMono.ttf', button_height=1.5, popup=0, clear_selected_on_enable=False)
    def input(key):
        if key == 'space':
            bl.button_dict = {
                'one' :     None,
                'two' :     default,
                'tree' :    Func(test, 3, 4),
                'four' :    Func(test, b=3, a=4),
            }
        if key == 'o':
            bl.enabled = True

    bl.selected = 'button 7'

    bl.button_dict = {}

    app.run()
