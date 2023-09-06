def singleton(cls, **kwargs):
    def getinstance(**kwargs):
        if not hasattr(cls, '_instance') or not cls._instance:
            cls._instance = cls(**kwargs)
        return cls._instance

    return getinstance


if __name__ == '__main__':
    from ursina import Ursina
    class Game(Ursina):
        pass
