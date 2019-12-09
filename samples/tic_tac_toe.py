from ursina import *


app = Ursina()

camera.orthographic = True
camera.fov = 4
camera.position = (1, 1)
Text.default_resolution *= 2

# for y in range(3):
#     for x in range(3):
#         b = Button(parent=scene, position=(x,y))

# create a matrix of buttons
board = [[Button(parent=scene, position=(x,y), color=color.color(0,0,0,.8)) for x in range(3)] for y in range(3)]

player_name = 'o'
player_color = color.azure
cursor = Tooltip(player_name, color=player_color, origin=(0,0), scale=4, enabled=True)
cursor.background.color = color.clear
bg = Entity(parent=scene, model='quad', texture='shore', scale=(16,8), z=10, color=color.light_gray)
mouse.visible = False


def input(key):
    global player_name, player_color, cursor

    if key == 'left mouse down' and mouse.hovered_entity:
        b = mouse.hovered_entity
        b.text = player_name
        b.color = player_color
        b.collision = False
        check_for_victory()

        if player_name == 'o':
            player_name = 'x'
            player_color = color.orange
        else:
            player_name = 'o'
            player_color = color.azure

        cursor.text = player_name


def check_for_victory():
    global board, cursor, player_name, player_color
    name = player_name

    won = (
    (board[0][0].text == name and board[1][0].text == name and board[2][0].text == name) or # across the bottom
    (board[0][1].text == name and board[1][1].text == name and board[2][1].text == name) or # across the middle
    (board[0][2].text == name and board[1][2].text == name and board[2][2].text == name) or # across the top
    (board[0][0].text == name and board[0][1].text == name and board[0][2].text == name) or # down the left side
    (board[1][0].text == name and board[1][1].text == name and board[1][2].text == name) or # down the middle
    (board[2][0].text == name and board[2][1].text == name and board[2][2].text == name) or # down the right side
    (board[0][0].text == name and board[1][1].text == name and board[2][2].text == name) or # diagonal /
    (board[0][2].text == name and board[1][1].text == name and board[2][0].text == name))   # diagonal \

    if won:
        print('winner is:', name)
        destroy(cursor)
        mouse.visible = True
        Panel(z=1, scale=10, model='quad')
        t = Text('player\n'+name+'\nwon!', scale=3, origin=(0,0), background=True)
        t.create_background(padding=(.5,.25), radius=Text.size/2)
        t.background.color = player_color.tint(-.2)


app.run()
