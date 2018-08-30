class Hit():
    def __init__(self, **kwargs):
        super().__init__()

        for key, value in kwargs.items():
            setattr(self, key, value)

    # hit
    # entity
    # distance
    # point
    # world_point
    # normal
    # world_normal
