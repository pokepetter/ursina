from ursina import *



app = Ursina(forced_aspect_ratio=.6)


bg = Entity(model='quad', scale=(30, 50), texture='grass', color=hsv(0,0,.2))
player = Entity(model=Circle(3), color=color.azure, speed=8, y=-.4, z=-1)
player.bullet_renderer = Entity(model=Mesh(mode='point', thickness=.2), texture='circle', color=color.yellow)

scene.fog_density = (10,50)
ec = EditorCamera(rotation_x=-20)


def shoot():
    player.bullet_renderer.model.vertices.append(player.position)

shoot_cooldown = .1
shoot_sequence = Sequence(Func(shoot), Wait(shoot_cooldown), loop=True)


def update():
    move_direction = Vec2(held_keys['d']-held_keys['a'], held_keys['w']-held_keys['s']).normalized()
    player.position += move_direction * player.speed * time.dt
    bg.texture_offset += Vec2(0, time.dt)

    for i, bullet in enumerate(player.bullet_renderer.model.vertices):
        player.bullet_renderer.model.vertices[i] += Vec3(0, time.dt * 10, 0)
        for enemy in enemies:
            if distance_2d(bullet, enemy) < .5:
                enemy.hp -= 1
                enemy.blink(color.white)
                if enemy.hp <= 0:
                    enemies.remove(enemy)
                    destroy(enemy)
                    # todo: add explosion particles and sound effect
                player.bullet_renderer.model.vertices.remove(bullet)

                print('a')

    if len(player.bullet_renderer.model.vertices):
        player.bullet_renderer.model.vertices = player.bullet_renderer.model.vertices[-100:]  # max bullets

    player.bullet_renderer.model.generate()


def input(key):
    if key == 'space':
        shoot_sequence.start()
    if key == 'space up':
        shoot_sequence.paused = True




enemies = []
enemy = Entity(model=Circle(3), rotation_z=180, position=(0, 16), color=color.red, z=-1, speed=3, hp=5)
enemies.append(enemy)

def enemy_update():
    for e in enemies:
        e.position += e.up * enemy.speed * time.dt



enemy_handler = Entity(update=enemy_update)

app.run()
