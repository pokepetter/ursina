"""
ursina/prefabs/animator.py

This file defines the Animator class, which is used to manage and control animations in the Ursina engine.
The Animator class allows switching between different animations and handles enabling/disabling of entities
based on the current animation state.

Dependencies:
- Ursina engine
"""

from ursina import *


class Animator:
    """
    The Animator class is used to manage and control animations in the Ursina engine.

    Attributes:
        animations (dict): A dictionary of animations with state names as keys and entities as values.
        pause_disabled (bool): A flag indicating whether to pause disabled animations.
        start_state (str): The initial state of the animator.
        _state (str): The current state of the animator.

    Methods:
        state(): Get or set the current state of the animator.
    """

    def __init__(self, animations=None, start_state='', pause_disabled=True):
        """
        Initialize the Animator object.

        Args:
            animations (dict): A dictionary of animations with state names as keys and entities as values.
            start_state (str): The initial state of the animator (default is an empty string).
            pause_disabled (bool): A flag indicating whether to pause disabled animations (default is True).
        """
        self.animations = animations    # Dictionary of animations
        self.pause_disabled = pause_disabled

        if not start_state and self.animations:
            start_state = list(self.animations)[0]

        self.start_state = start_state
        self._state = None
        self.state = start_state

    @property
    def state(self):
        """
        Get the current state of the animator.

        Returns:
            str: The current state of the animator.
        """
        return self._state

    @state.setter
    def state(self, value):
        """
        Set the current state of the animator. This will enable the corresponding animation
        and disable all other animations.

        Args:
            value (str): The new state of the animator.
        """
        if not value in self.animations:
            print(self, 'has no animation:', value)

        elif not self._state == value:
            # Only show the set state and disable the rest
            for name, entity in self.animations.items():
                if entity:
                    entity.enabled = value == name
                    if self.pause_disabled and hasattr(entity, 'pause') and not entity.enabled:
                        [anim.pause() for anim in entity.animations]

            entity = self.animations[value]
            if entity:
                if hasattr(entity, 'start') and callable(entity.start):
                    entity.start()

                if hasattr(entity, 'animations'):
                    [anim.start() for anim in entity.animations]

        self._state = value


if __name__ == '__main__':
    app = Ursina()
    # texture_importer.textureless=True
    anim = Animation('ursina_wink', loop=True, autoplay=False)
    a = Animator(
        animations = {
            'lol' : Entity(model='cube', color=color.red),
            'yo' : Entity(model='cube', color=color.green, x=1),
            'help' : anim,
        }
    )
    a.state = 'yo'

    Text('press <red>1<default>, <green>2<default> or <violet>3<default> to toggle different animator states', origin=(0,-.5), y=-.4)

    def input(key):
        if key == '1':
            a.state = 'lol'
        if key == '2':
            a.state = 'yo'
        if key == '3':
            a.state = 'help'
            print(anim.enabled)

    app.run()
