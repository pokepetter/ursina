import ursina


class Paddle(ursina.Entity):
    '''
    Player paddle
    '''

    def __init__(self, x: float, control_keys: tuple) -> None:
        '''
        Initialize self

            Parametrs:
                x (float): object position along x coordinate
                control_keys (tuple): enumeration of control keys
        '''
        super().__init__(
            model='quad',
            scale=(1/35, 7/35),
            collider='box',
            x=x,
            color=ursina.color.random_color()
        )
        self.control_keys = control_keys
        self.speed = 1
        self.score = 0

    def update(self) -> None:
        '''Updates the object's state when control keys are entered'''

        # If the key is pressed, the value in the
        # held_keys dictionary corresponding to the key is 1
        up_key = ursina.held_keys[self.control_keys[0]]
        down_key = ursina.held_keys[self.control_keys[1]]

        if (self.y + self.scale_y/2) >= 0.5:
            down_key = 1
        elif (self.y - self.scale_y/2) <= -0.5:
            up_key = 1

        # If the upper key is pressed, then the expression in brackets
        # is equal to a positive one, if the lower key, then a negative one.
        # This sets the direction of movement
        self.y += (up_key - down_key) * ursina.time.dt * self.speed

    def reload(self) -> None:
        '''Sets initial parameters'''
        self.y = 0
        self.score = 0
