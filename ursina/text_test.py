
from ursina import *
app = Ursina()
t = '''this is
some text in a
paragraph'''.upper()
# Text(t)
Entity(model='quad', scale=(.025, .025), color=color.orange)

split_text = t.split('\n')
text_parts = list()
for t in split_text:
    text_parts.append(Text(t))

origin = (0, 0)
# height = text_parts[0].height
# from panda3d.core import TextNode
# height = TextNode('asdhkøq381FMGGgj').get_height()
text_parts[0].text_nodes[0].getHeight()
printvar(height)

# for t in text_parts:
#     t.y -= height/2

camera.orthographic = True
camera.fov = 5
app.run()
# lengths = (6, 14, )
