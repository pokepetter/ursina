def singleton(cls):
    if not isinstance(cls, type):
        raise TypeError(f"@singleton must be used on a class, but got {type(cls).__name__}")

    class SingletonWrapper(cls):
        _instance = None  # Store instance at the wrapper level

        def __new__(subcls, *args, **kwargs):
            if subcls is not SingletonWrapper:  # Prevent subclassing
                raise TypeError(f"Cannot inherit class {cls.__name__} because it is a singleton. Use composition instead.")
            if SingletonWrapper._instance is None:
                SingletonWrapper._instance = super().__new__(cls)
            return SingletonWrapper._instance

    # Prevent subclassing explicitly
    def prevent_subclassing(subcls, **kwargs):
        raise TypeError(f"Cannot inherit class {cls.__name__} because it is a singleton. Use composition instead.")

    cls.__init_subclass__ = classmethod(prevent_subclassing)

    return SingletonWrapper



if __name__ == '__main__':
    from ursina import Ursina
    app = Ursina()
    app2 = Ursina()

    print(app == app2)

    class Game(Ursina):
        pass
