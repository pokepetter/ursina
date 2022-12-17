import ursina

from menu import Menu
from paddle import Paddle
from ball import Ball


class Pong(ursina.Entity):
    '''
    Creates basic objects, sets application options, and manages gameplay
    '''

    def __init__(self, is_music_on: bool, is_sound_on: bool) -> None:
        super().__init__()

        self.is_music_on = is_music_on
        self.is_sound_on = is_sound_on

        self.set_app_options(title='PyPong', fullscreen=True)
        self.build_game_objects()

    def set_app_options(self, title: str, fullscreen: bool) -> None:
        '''Sets application options'''
        ursina.window.title = title
        ursina.window.fullscreen = fullscreen
        ursina.window.fps_counter.enabled = False

        # In this projection mode, the size of the object
        # in the displayed image remains constant
        ursina.camera.orthographic = True

        # Defines the angle you can see around the center of the camera
        ursina.camera.fov = 1

    def build_game_objects(self) -> None:
        '''Creates basic game objects'''
        background = ursina.Entity(
            model='quad', texture=r'assets\images\background.png',
            scale=(ursina.window.aspect_ratio, 1)
        )

        self.background_music = ursina.Audio(
            r'assets\music\background.mp3', loop=True, autoplay=self.is_music_on,
            volume=0.25
        )

        self.point_sound = ursina.Audio(
            r'assets\sounds\point.mp3', autoplay=False
        )

        self.hit_sound = ursina.Audio(
            r'assets\sounds\hit.mp3', volume=3, autoplay=False
        )

        self.left_paddle = Paddle(x=-0.85, control_keys=('w', 's'))
        self.right_paddle = Paddle(
            x=0.85, control_keys=('up arrow', 'down arrow')
        )
        self.ball = Ball()
        self.ball.ignore = True

        self.right_wall = 0.5 * ursina.window.aspect_ratio - self.ball.scale_x/2
        self.left_wall = self.right_wall * (-1)

        self.left_paddle_scoreboard = ursina.Text(
            text=str(self.left_paddle.score), scale=3, x=-0.5, y=0.4
        )
        self.right_paddle_scoreboard = ursina.Text(
            text=str(self.right_paddle.score), scale=3, x=0.5, y=0.4
        )

    def update(self) -> None:
        '''Manages the game loop'''
        self.ball.collide_with_wall()
        self.ball.collide_with_paddle(
            self.left_paddle, self.right_paddle, self.is_sound_on, self.hit_sound
        )
        self.ball_hitting_the_goal()

    def update_score(self, paddle: Paddle, scoreboard: ursina.Text) -> None:
        '''Updates score'''
        if self.is_sound_on:
            self.point_sound.play()

        paddle.score += 1
        scoreboard.text = str(paddle.score)
        self.ball.reload()

    def ball_hitting_the_goal(self) -> None:
        '''
        Tracks the ball hitting the goal and increases the points for the corresponding player.
        Restarts the ball.

        About calculating window borders
        --------------------------------
        aspect_ratio = width / height, this implies:
            width = height * aspect_ratio

        Since the center of the window has a coordinate of (0, 0), to calculate the coordinate
        of the window border (right or left), you need take only half
        the width with the desired sign:
            width = ±(0.5 * (height * aspect_ratio))

        Window height = 1, so the expression is:
            window_border_coordinate (right or left) = ±(0.5 * aspect_ratio)
        '''

        if self.ball.x < self.left_wall:
            self.update_score(self.right_paddle, self.right_paddle_scoreboard)
        elif self.ball.x > self.right_wall:
            self.update_score(self.left_paddle, self.left_paddle_scoreboard)

    def reload(self) -> None:
        '''Sets initial parameters'''
        self.ball.reload()
        self.ball.ignore = True
        self.left_paddle.reload()
        self.right_paddle.reload()
        self.left_paddle_scoreboard.text = '0'
        self.right_paddle_scoreboard.text = '0'

    def input(self, key) -> None:
        '''Processes input'''
        if key == 'r':
            self.reload()
        elif key == 'p':
            self.ball.ignore = not self.ball.ignore
        elif key == 'm':
            if self.is_music_on:
                self.background_music.stop()
                self.is_music_on = False
            else:
                self.background_music.play()
                self.is_music_on = True
        elif key == 'v':
            self.is_sound_on = not self.is_sound_on


if __name__ == '__main__':
    app = ursina.Ursina()

    def start():
        Pong(menu.is_music_on, menu.is_sound_on)
        menu.destroy()

    menu = Menu()
    menu.play_button.on_click = start

    app.run()
