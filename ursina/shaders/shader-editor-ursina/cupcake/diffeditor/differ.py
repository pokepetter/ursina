import difflib


class Differ(difflib.Differ):
    def __init__(self, master, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.master = master
        self.base = master.base

    def get_diff(self, lhs, rhs):
        return self.compare(lhs, rhs)
