from typing import Tuple, Literal


RenderMode = Literal["default", "wireframe", "colliders", "normals"]
WindowType = Literal["default", "offscreen", "onscreen"]

# This two are practically useless, but I'm keeping them because I'm too lazy to refactor it
OptionalString = str
OptionalBool = bool

WindowSize = Tuple[int, int]


