from ursina import *

class DebugMenu(Draggable):
    def __init__(self, target):
        super().__init__()
        self.target = target
        self.scale = (.2, .025)
        self.text = '<orange>' + target.__class__.__name__
        self.draw_functions()

    def draw_functions(self):
        for c in self.children:
            destroy(c)
        for i, f in enumerate([func for func in dir(self.target.__class__)
        if callable(getattr(self.target.__class__, func))
        and not func.startswith("__")]):
            # print('functions:', f)
            b = Button(
                parent = self,
                text = f + '()',
                y = -i - 1,
                on_click = getattr(self.target, f)
                )
