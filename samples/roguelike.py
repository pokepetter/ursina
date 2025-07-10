from ursina import *


app = Ursina()

level = '''
###....#
#....###
##.....#
##.....#
##.....#
.#####.#
'''.strip()

grid = list(reversed(level.split('\n'))) # flip it vertically so the last line is the first element

window.color = color.black
camera.orthographic = True
camera.fov = 10
camera.position = (4,2)

level_geometry = Entity(model=Mesh(mode='point', thickness=.5), texture='circle')
for y, line in enumerate(grid):
    for x, char in enumerate(line):
        if char == '#':
            level_geometry.model.vertices.append(Vec3(x,y,0))

level_geometry.model.generate()
level_geometry.model.set_render_mode_perspective(True)

player = Button(parent=scene, text='@', text_color=color.lime, position=(4,2,-.1))


def input(key):
    if key in ('a', 'a hold'):
        walk((-1,0))
    if key in ('d', 'd hold'):
        walk((1,0))
    if key in ('w', 'w hold'):
        walk((0,1))
    if key in ('s', 's hold'):
        walk((0,-1))


def walk(direction):
    target_x = int(player.x + direction[0])
    target_y = int(player.y + direction[1])

    collided = grid[target_y][target_x] in ('#', '|', '/', '\\', 'A')

    if not collided:
        player.position += direction


app.run()
