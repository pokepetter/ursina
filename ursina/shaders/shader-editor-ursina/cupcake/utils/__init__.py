"""
Various types of widgets/functions used across the editor
"""

from .directorytree import DirectoryTree
from .canvas import Canvas
from .frame import Frame
from .filetype import FileType
from .label import Label
from .scrollbar import Scrollbar
from .scrollableframe import ScrollableFrame
from .tree import Tree
from .menubutton import Menubutton
from .toplevel import Toplevel
from .text import Text

@staticmethod
def clamp(value, min_val, max_val):
    return min(max(min_val, value), max_val)
