from ursina import Entity, Sequence, Func, Wait


class SpriteSheetAnimation(Entity):
    def __init__(self, texture, animations, tileset_size=[4,1], fps=12, model='quad', autoplay=True, **kwargs):
        kwargs['model'] = model
        kwargs['texture'] = texture
        kwargs['tileset_size'] = tileset_size
        super().__init__(**kwargs)

        self.animations = animations # should be a dict

        for key, value in self.animations.items():
            start_coord, end_coord = value
            s = Sequence(loop=True)

            for y in range(start_coord[1], end_coord[1]+1):
                for x in range(start_coord[0], end_coord[0]+1):
                    s.extend([
                        Func(setattr, self, 'tile_coordinate', (x,y)),
                        Wait(1/fps)
                    ])
            self.animations[key] = s


    def play_animation(self, animation_name):
        if not self.animations:
            return

        [anim.pause() for anim in self.animations.values()]

        self.animations[animation_name].start()


if __name__ == '__main__':
    '''
    (0,0) is in bottom left
    '''
    from ursina import Ursina
    app = Ursina()
    player_graphics = SpriteSheetAnimation('sprite_sheet', tileset_size=(4,4), fps=6, animations={
        'idle' : ((0,0), (0,0)),
        'walk_up' : ((0,0), (3,0)),
        'walk_right' : ((0,1), (3,1)),
        'walk_left' : ((0,2), (3,2)),
        'walk_down' : ((0,3), (3,3)),
        }
        )
    def input(key):
        if key == 'w':
            player_graphics.play_animation('walk_up')
        elif key == 's':
            player_graphics.play_animation('walk_down')
        elif key == 'd':
            player_graphics.play_animation('walk_right')
        elif key == 'a':
            player_graphics.play_animation('walk_left')

        # elif key == 'w up':
        #     player_graphics.play_animation('idle')

    # print(player_graphics.animations['walk_up'].funcs)

    Entity(model='quad', texture='sprite_sheet', x=-1)
    app.run()
