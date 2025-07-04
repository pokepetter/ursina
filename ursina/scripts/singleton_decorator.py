def singleton(cls):
    def get_instance(*args, **kwargs):
        if not hasattr(cls, '_singleton_instance') or not cls._singleton_instance:
            cls._singleton_instance = cls(*args, **kwargs)
        return cls._singleton_instance

    return get_instance


if __name__ == '__main__':
    from ursina.ursinastuff import _test

    class MyBaseClass:
        def __init__(self, name):
            self.name = name

    @singleton
    class DecoratedClass(MyBaseClass):
        def __init__(self, name='decorated_class'):
            super().__init__(name)

    app = DecoratedClass()
    app_2 = DecoratedClass()
    _test(app == app_2)

    # # this won't work
    # class Game(DecoratedClass):
    #     pass
