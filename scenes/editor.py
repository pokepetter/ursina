import sys
sys.path.append("..")
from pandaeditor import *
# import prefabs

class Editor():
    # panel = load_prefab('panel')
    # panel.color = color.dark_gray
    # panel.position = (0, 0, 0)
    # panel.scale = (1,1,1)
    # panel.texture = 'textures/editor_background.png'

    toolbar = load_prefab('panel')
    toolbar.origin = (0, 0, .5)
    toolbar.position = (0, 0, .49)
    toolbar.scale = (1, 1, .025)
    toolbar.color = color.gray

    for i in range(4):
        button = load_prefab('button')
        button.parent = toolbar
        button.origin = (-.5, 0, 0)
        button.position = (-.487 + (i * .061), 0, 0)
        button.scale = (.06, 1, 1)
        button.color = color.orange
        button.text = 'button'
        # button.text.color = color.black

    sidebar = load_prefab('panel')
    sidebar.origin = (-.5, 0, -0.0)
    sidebar.position = (-.5, 0, 0)
    sidebar.scale = (.04, 1, .9)
    # sidebar.color = color.gray
    sidebar.color = color.black33
    # test.color = hsv_color(210, 1, 1)
    # print(color.hsv_color(90, 1, 1))

    scene_list = load_prefab('panel')
    # scene_list.origin = (-.5, 0, -0.0)
    scene_list.position = (-.0, 0, -0.0)
    scene_list.scale = (.4, 1, .5)
    scene_list.color = color.black33

    text = load_prefab('text')
    text.parent = scene_list
    text.position = (0, -.1, 0)
    text.scale = (.9,.9,.9)
    t = 'test text'
#     t = '''zxcvb nmasd ghj qwetyutuoi phklz xcvbnma sdghjqwetyutuo iphkl xcvbnm
# asdgh jqwetyu tuoiphklzxcv bnma s ghjqw et yutu oiph klzxcvbnm asdgh jqwe tyut uoi phkl
# zxcvb nmasd ghj qwetyutuoi phklz xcvbnma sdghjqwetyutuo iphkl xcvbnm
# asdgh jqwetyu tuoiphklzxcv bnma s ghjqw et yutu oiph klzxcvbnm asdgh jqwe tyut uoi phkl
# zxcvb nmasd ghj qwetyutuoi phklz xcvbnma sdghjqwetyutuo iphkl xcvbnm
# asdgh jqwetyu tuoiphklzxcv bnma s ghjqw et yutu oiph klzxcvbnm asdgh jqwe tyut uoi phkl'''
    # for i in range(50):
    #     t += random.choice('zxcvbnmasdghjqwetyutuoiphkl,n')
    text.text = t
    text.color = color.blue
