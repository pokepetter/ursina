class every:
    '''@every  decorator for calling a function on an Entity every n seconds.

        example:
        @every(.1)
        def fixed_update():
            print('check collision')

        Using the @every decorator is the same as doing this in __init__() (on Entity):
        self.animations.append(Sequence(Func(self.fixed_update), Wait(.1), loop=True, started=True))
        The Sequence will call the function every .1 second, while adding it to
        self.animations ensures the Sequence gets cleaned up when the Entity gets destroyed.
    '''
    decorated_methods = []  # store decorated methods here

    def __init__(self, interval):
        # print('asdlkjasldkasjdlkj')
        self.interval = interval

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            # print(f"-----------Calling {func.__name__} every {self.interval} seconds")
            return func(*args, **kwargs)

        wrapper._every = self  # add _every attribute to the decorated method
        wrapper._func = func
        every.decorated_methods.append(wrapper)  # store the decorated method
        return wrapper


def get_class_name(func):
    qualname_parts = func.__qualname__.split('.')
    class_name = qualname_parts[-2] if len(qualname_parts) > 1 else None
    return class_name


if __name__ == '__main__':
    from ursina import*
    app = Ursina()

    # @every(.1)
    # def test():
    #     print('test')


    class Enemy(Entity):
        @every(.2)
        def attack(self):
            print('attack')

    enemy = Enemy(enabled=1)

    # test that it gets pause when disabling the entity
    def input(key):
        if key == 'space':
            enemy.enabled = not enemy.enabled
            print(enemy.enabled)

    app.run()
