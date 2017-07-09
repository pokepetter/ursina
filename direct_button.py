from panda3d.core import NodePath
from panda3d.core import TextNode
from direct.gui.DirectGui import *

global cm

def create_button(text='empty', origin=(0,0,0), position=(0,0,0), size=(1,0,1), scale=0.04):
    button_text = TextNode("button_text")
    button_text.setText(text)
    button_text.setTextColor((.7, .7, .7, 1))
    button_text.setCardColor(.1, .1, .1, 1)
    button_text.setAlign(TextNode.ACenter)
    button_text.setCardAsMargin(size[0]*scale, size[0]*scale, size[2]*scale, size[2]*scale)
    button_text.setCardDecal(True)
    button_normal = NodePath(cm.generate())
    button_normal.attachNewNode(button_text)
    # font = loader.loadFont('my_font.egg')
    # button_text.setFont(font)

    # highlighted
    button_text_hover = TextNode("button_text_hover")
    button_text_hover.setText(text)
    button_text_hover.setTextColor((.9, .9, .9, 1))
    button_text_hover.setCardColor(.15, .15, .15, 1)
    button_text_hover.setAlign(TextNode.ACenter)
    button_text_hover.setCardAsMargin(size[0], size[0], size[2], size[2])
    button_text_hover.setCardDecal(True)
    button_highlighted = NodePath(cm.generate())
    button_highlighted.attachNewNode(button_text_hover)

    # pressed
    button_text_pressed = TextNode("button_text_pressed")
    button_text_pressed.setText(text)
    button_text_pressed.setTextColor((.8, .9, .9, 1))
    button_text_pressed.setCardColor(.0, .0, .0, 1)
    button_text_pressed.setAlign(TextNode.ACenter)
    button_text_pressed.setCardAsMargin(size[0], size[0], size[2], size[2])
    button_text_pressed.setCardDecal(True)
    button_pressed = NodePath(cm.generate())
    button_pressed.attachNewNode(button_text_pressed)

    button = DirectButton(
        relief = None,
        pressEffect = 0,
        geom = (button_normal, button_pressed, button_highlighted, button_normal),
        scale = scale,
        # pad = (scale * 3, scale * 1),
        # pos = (position[0] + (origin[0] * -size[0] * scale / 2),
        pos = (position[0],
                0,
                position[2]),
    )
    button.reparentTo(aspect2d)
    return button
