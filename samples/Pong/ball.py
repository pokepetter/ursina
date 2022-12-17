import ursina

from random import choice

from paddle import Paddle


class Ball(ursina.Entity):
    '''
    Ping-pong ball
    '''

    def __init__(self) -> None:
        super().__init__(
            model='circle',
            scale=0.05,
            collider='box',
            color=ursina.color.hex('#D57BFF')
        )
        self.reload()

    def update(self) -> None:
        '''Implements object movement'''
        self.x += self.speed_x * ursina.time.dt
        self.y += self.speed_y * ursina.time.dt

    def collide_with_wall(self) -> None:
        '''
        Tracks the collision of the object with the top and bottom borders
        of the window and changes the direction of movement.
        Top border = 0.5, bottom = -0.5 since window height = 1
        '''
        top_wall = 0.5 - self.scale_y/2
        bottom_wall = top_wall * (-1)

        if (
            (self.y <= bottom_wall and self.speed_y < 0) or
            (self.y >= top_wall and self.speed_y > 0)
        ):
            self.speed_y *= -1

    def collide_with_paddle(
        self, left_paddle: Paddle, right_paddle: Paddle,
        is_sound_on: bool, hit_sound: ursina.Audio
    ) -> None:
        '''Tracks object collisions with paddles and changes the direction of movement'''
        hit_info = self.intersects()
        collision_tolerance = 0.2

        if hit_info.hit:
            # Checking the direction of the ball prevents it from getting stuck in the paddle
            if hit_info.entity is right_paddle and self.speed_x > 0:
                # When the sides touch each other, the absolute value of
                # the difference in their coordinates is approximately zero.
                # This allows you to determine the side of the collision, and,
                # if necessary, change the direction of the ball
                if abs(self.right[0] - right_paddle.left[0]) < collision_tolerance:
                    if is_sound_on:
                        hit_sound.play()
                    self.speed_x *= (-1)
                    self.speed_y *= choice((-1, 1))

            elif hit_info.entity is left_paddle and self.speed_x < 0:
                if abs(self.left[0] - left_paddle.right[0]) < collision_tolerance:
                    if is_sound_on:
                        hit_sound.play()
                    self.speed_x *= (-1)
                    self.speed_y *= choice((-1, 1))

    def reload(self) -> None:
        '''Sets initial parameters'''
        self.x = self.y = 0
        self.speed_x = self.speed_y = 1

        directions = (-1, 1)
        self.speed_x *= choice(directions)
        self.speed_y *= choice(directions)
