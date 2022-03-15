from ursina import *



app = Ursina(forced_aspect_ratio=.6)


bg = Entity(model='quad', scale=(30, 50), texture='grass', color=hsv(0,0,.2))
player = Entity(model=Circle(3), color=color.azure, speed=8, y=-.4, z=-1)
player.bullet_renderer = Entity(model=Mesh(mode='point', thickness=.2), texture='circle', color=color.yellow)

scene.fog_density = (10,50)
ec = EditorCamera(rotation_x=-30)
# camera.parent = player
# camera.z = -10

def update():
    move_direction = Vec2(held_keys['d']-held_keys['a'], held_keys['w']-held_keys['s']).normalized()
    print(move_direction)
    player.position += move_direction * player.speed * time.dt

    bg.texture_offset += Vec2(0, time.dt)

    if mouse.left:
        # player_bullets.append(player.position.xy)
        player.bullet_renderer.model.vertices.append(player.position)

    for i, e in enumerate(player.bullet_renderer.model.vertices):
        player.bullet_renderer.model.vertices[i] += Vec3(0, time.dt * 10, 0)

    player.bullet_renderer.model.generate()




enemies = []
enemy = Entity(model=Circle(3), rotation_y=180, y=.5)
enemies.append(enemy)

def enemy_update():
    for e in enemies:
        e.position += e.up



enemy_handler = Entity(update=enemy_update)

app.run()
