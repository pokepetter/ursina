def singleton(cls):
    class SingletonProxy:
        _singleton_instance = None

        def __new__(proxy_cls, *args, **kwargs):
            if SingletonProxy._singleton_instance is None:
                SingletonProxy._singleton_instance = cls(*args, **kwargs)
            return SingletonProxy._singleton_instance

        def __init_subclass__(sub_cls, **kwargs):
            raise TypeError(
                f"Cannot subclass @{singleton.__name__}-decorated class '{cls.__name__}'."
            )

    SingletonProxy.__name__ = cls.__name__
    SingletonProxy.__doc__ = cls.__doc__
    return SingletonProxy


if __name__ == '__main__':

    class MyBaseClass:
        def __init__(self, name):
            self.name = name

    @singleton
    class DecoratedClass(MyBaseClass):
        def __init__(self, name='decorated_class'):
            super().__init__(name)

    app = DecoratedClass()
    app_2 = DecoratedClass()
    assert(app == app_2)

    # this won't work
    class Game(DecoratedClass):
        pass
