from ursina import *


# t = TextBox('text')





if __name__ == '__main__':
    app = Ursina()
    t = Text('Hi there <lime>Pebble<default>! How is it going? Have you found all of your <orange>cats <default>yet?')
    t.wordwrap = 50
    # t.background.origin = (.5, 0)
    # text = t.text
    # t.text = ''
    # for i in range(len(text)):
    #     invoke
    # print(t.text)
    # t.text_entity.enabled = False
    # invoke(setattr, t.text_entity, 'enabled', True, delay=1)
    # invoke(print, 'yoloy', delay=3)
    # t.animate_scale((0,0), 2)
    app.run()
