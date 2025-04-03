"""
ursina/prefabs/button_group.py

This module defines the ButtonGroup class, which is used to create a group of buttons with selection capabilities.
It allows for single or multiple selections, and provides options for customizing the appearance and behavior of the buttons.

Dependencies:
- ursina.Entity
- ursina.Button
- ursina.camera
- ursina.color
- ursina.Text
- ursina.window
- ursina.mouse
- ursina.destroy
- ursina.Vec2
- ursina.inverselerp
- ursina.scripts.grid_layout
- ursina.scripts.property_generator
"""

from ursina import Entity, Button, camera, color, Text, window, mouse, destroy, Vec2, inverselerp
from ursina.scripts.grid_layout import grid_layout
from ursina.scripts.property_generator import generate_properties_for_class


@generate_properties_for_class()
class ButtonGroup(Entity):
    """
    The ButtonGroup class is used to create a group of buttons with selection capabilities.
    It allows for single or multiple selections, and provides options for customizing the appearance and behavior of the buttons.

    Attributes:
        default_selected_color (color): The default color for selected buttons.
        default_highlight_selected_color (color): The default highlight color for selected buttons.
        buttons (list): A list of buttons in the group.
        selected (list): A list of selected buttons.
        deselected_color (color): The color for deselected buttons.
        highlight_color (color): The highlight color for buttons.
        selected_color (color): The color for selected buttons.
        highlight_selected_color (color): The highlight color for selected buttons.
        min_selection (int): The minimum number of selections allowed.
        max_selection (int): The maximum number of selections allowed.
        origin (Vec2): The origin point for the button group layout.
        spacing (tuple): The spacing between buttons.
        max_x (int): The maximum number of buttons in a row.
        label_text_entity (Text): The text entity for the label.
        options (list): The list of options for the buttons.
    """
    default_selected_color = color.azure
    default_highlight_selected_color = default_selected_color

    def __init__(self, options, default='', min_selection=1, max_selection=1, origin=(-.5,.5), spacing=(0.025,0), label='', max_x=99, **kwargs):
        """
        Initialize the ButtonGroup.

        Args:
            options (list): The list of options for the buttons.
            default (str, optional): The default selected option. Defaults to ''.
            min_selection (int, optional): The minimum number of selections allowed. Defaults to 1.
            max_selection (int, optional): The maximum number of selections allowed. Defaults to 1.
            origin (tuple, optional): The origin point for the button group layout. Defaults to (-.5,.5).
            spacing (tuple, optional): The spacing between buttons. Defaults to (0.025,0).
            label (str, optional): The label for the button group. Defaults to ''.
            max_x (int, optional): The maximum number of buttons in a row. Defaults to 99.
            **kwargs: Additional keyword arguments for customization.
        """
        super().__init__()
        self.buttons = []
        self.selected = []

        self.deselected_color =         Button.default_color
        self.highlight_color =          Button.default_highlight_color if Button.default_highlight_color is not None else Button.default_color.tint(.2)
        self.selected_color =           ButtonGroup.default_selected_color
        self.highlight_selected_color = ButtonGroup.default_highlight_selected_color

        self.min_selection = min_selection
        self.max_selection = max(min_selection, max_selection)
        self.origin = origin
        self.spacing = spacing
        self.max_x = max_x
        self.label_text_entity = None
        if label:
            self.label = label

        self.options = options

        self.parent = camera.ui
        self.scale = Text.size * 2


        for key, value in kwargs.items():
            setattr(self, key, value)

        if default:
            for b in [e for e in self.buttons if e.value == default]:
                self.select(b)
        else:
            for i in range(min_selection):
                self.select(self.buttons[i])

    def options_setter(self, value):
        """
        Setter for the options attribute. Updates the button layout.

        Args:
            value (list): The list of options for the buttons.
        """
        self._options = value
        self.layout()

    def origin_setter(self, value):
        """
        Setter for the origin attribute. Updates the button layout.

        Args:
            value (tuple): The origin point for the button group layout.
        """
        if not isinstance(value, Vec2):
            value = self._list_to_vec(value)

        self._origin = value
        if not self.buttons:
            return
        self.layout()

    def value_getter(self):
        """
        Getter for the value attribute. Returns the selected value(s).

        Returns:
            str or list: The selected value(s).
        """
        if self.max_selection == 1:
            return self.selected[0].value

        return [b.value for b in self.selected]

    def value_setter(self, value):
        """
        Setter for the value attribute. Selects the specified value(s).

        Args:
            value (str or list): The value(s) to select.
        """
        [self.select(b) for b in self.buttons if b.value in value]

    def label_setter(self, value):
        """
        Setter for the label attribute. Updates the label text entity.

        Args:
            value (str): The label text.
        """
        if not self.label_text_entity:
            self.label_text_entity = Text(parent=self, world_scale=25/2, origin=(0,-.5), position=(0,0,-1), color=color.text_color)
        self.label_text_entity.text = value

    def layout(self):
        """
        Layout the buttons in the button group.
        """
        [destroy(c) for c in self.buttons]
        self.buttons = []
        longest_word = max(self.options, key=len) + '__' # padding
        width = Text.get_width(longest_word) / Text.size / 2

        for e in self.options:
            b = Button(parent=self, text=e, name=e, scale_x=width, scale_y=.9, highlight_scale=1, pressed_scale=1)
            b.value = e
            self.buttons.append(b)

        grid_layout(self.buttons, origin=self.origin.xy, spacing=self.spacing, max_x=self.max_x)
        if self.label_text_entity:
            self.label_text_entity.origin = Vec2(self.origin.x, -self.origin.y)
            self.label_text_entity.position = Vec2.zero
            if self.origin_y == 0:
                self.label_text_entity.origin = Vec2(-self.origin.x, 0)
            if self.origin == Vec2.zero:
                self.label_text_entity.x = -(width * min(len(self.buttons), self.max_x) * .5)
                self.label_text_entity.origin = Vec2(.5,0)

    def input(self, key):
        """
        Handle input events for the button group.

        Args:
            key (str): The input key.
        """
        if key == 'left mouse down' and mouse.hovered_entity in self.buttons:
            self.select(mouse.hovered_entity)

    def select(self, b):
        """
        Select a button in the button group.

        Args:
            b (Button): The button to select.
        """
        if b in self.selected and self.min_selection > 0 and len(self.selected) >= self.min_selection:
            return

        # add
        if b not in self.selected:
            b.color = self.selected_color
            b.highlight_color = self.highlight_selected_color
            self.selected.append(b)

            if len(self.selected) > self.max_selection:
                # remove oldest addition
                self.selected[0].color = self.deselected_color
                self.selected[0].highlight_color = self.highlight_color
                self.selected.pop(0)

        self.on_value_changed()

    def on_value_changed(self):
        """
        Called when the value of the button group changes.
        Assign a function to this to make something happen when the value changes.
        """
        pass


if __name__ == '__main__':
    from ursina import *
    app = Ursina()
    
    # # test setting custom default colors
    # Text.default_font = 'VeraMono.ttf'
    # color.text_color = color.orange
    # Button.default_highlight_color = color.blue
    # Button.default_color = color.turquoise
    # ButtonGroup.default_highlight_selected_color = color.white

    center = Entity(parent=camera.ui, model='circle', scale=.005, color=color.red, z=-1)
    gender_selection = ButtonGroup(('man', 'woman', 'other'), 
        origin=(-.5,0), 
        label='choose gender:', 
        max_x=1
        )

    def on_value_changed():
        print('set gender:', gender_selection.value)
    gender_selection.on_value_changed = on_value_changed


    window.color = color._32

    # test
    for e in [(-.5,.5), (0,.5), (.5,.5), (-.5,0), (0,0), (.5,0), (-.5,-.5), (0,-.5), (.5,-.5)]:
        Button(
            text='*',
            model='quad',
            text_origin=e,
            scale=.095,
            origin=(-.5,.5),
            position = window.top_left + Vec2(*e)*.2 + Vec2(.1,-.1),
            tooltip=Tooltip(str(e)),
            on_click=Func(setattr, gender_selection, 'origin', e),
        )
        
    app.run()
