from ursina import *

class EditorCamera(Entity):

    def __init__(self, **kwargs):
        camera.editor_position = camera.position
        super().__init__(name='editor_camera', eternal=True)

        self.gizmo = Entity(parent=self, model='sphere', color=color.orange, scale=.025, add_to_scene_entities=False)

        self.rotation_speed = 200
        self.pan_speed = Vec2(5, 5)
        self.move_speed = 10
        self.zoom_speed = .75
        self.rotate_around_mouse_hit = False

        for key, value in kwargs.items():
            setattr(self, key, value)

        self.start_position = self.position
        self.perspective_fov = camera.fov
        self.orthographic_fov = camera.fov
        self.on_destroy = self.on_disable
        self.hotkeys = {'toggle_orthographic':'p', 'center':'f'}


    def on_enable(self):
        camera.org_parent = camera.parent
        camera.org_position = camera.position
        camera.org_rotation = camera.rotation

        camera.parent = self
        camera.position = camera.editor_position
        camera.rotation = (0,0,0)


    def on_disable(self):
        camera.editor_position = camera.position
        camera.parent = camera.org_parent
        camera.position = camera.org_position
        camera.rotation = camera.org_rotation


    def input(self, key):
        if key == self.hotkeys['toggle_orthographic']:
            if not camera.orthographic:
                self.orthographic_fov = camera.fov
                camera.fov = self.perspective_fov
            else:
                self.perspective_fov = camera.fov
                camera.fov = self.orthographic_fov

            camera.orthographic = not camera.orthographic


        elif key == self.hotkeys['center']:
            if held_keys['shift']:
                # self.position = self.start_position
                self.animate_position(self.start_position, duration=.1, curve=curve.linear)

            elif mouse.world_point:
                self.animate_position(mouse.world_point, duration=.1, curve=curve.linear)
                # self.position = mouse.world_point


        elif key == 'scroll up' and not held_keys['control']:
            if not camera.orthographic:
                target_position = self.world_position
                if mouse.hovered_entity and not mouse.hovered_entity.has_ancestor(camera):
                    target_position = mouse.world_point

                self.world_position = lerp(self.world_position, target_position, self.zoom_speed * time.dt * 10)
                camera.z += self.zoom_speed * time.dt * (abs(camera.z)*.1) * 100
            else:
                camera.fov -= self.zoom_speed * 100 * time.dt * (abs(camera.z)*.1)

        elif key == 'scroll down' and not held_keys['control']:
            if not camera.orthographic:
                camera.world_position += camera.back * self.zoom_speed * 100 * time.dt * (abs(camera.z)*.1)
            else:
                camera.fov += self.zoom_speed * 100 * time.dt * (abs(camera.z)*.1)

        elif key == 'right mouse down' or key == 'middle mouse down':
            if mouse.hovered_entity and self.rotate_around_mouse_hit:
                org_pos = camera.world_position
                self.world_position = mouse.world_point
                camera.world_position = org_pos




    def update(self):
        if mouse.right:
            self.rotation_x -= mouse.velocity[1] * self.rotation_speed
            self.rotation_y += mouse.velocity[0] * self.rotation_speed

            self.position += camera.right * held_keys['d'] * (self.move_speed + (self.move_speed * held_keys['shift']) - (self.move_speed*.9 * held_keys['alt'])) * time.dt
            self.position += camera.left * held_keys['a'] * (self.move_speed + (self.move_speed * held_keys['shift']) - (self.move_speed*.9 * held_keys['alt'])) * time.dt
            self.position += camera.up * held_keys['e'] * (self.move_speed + (self.move_speed * held_keys['shift']) - (self.move_speed*.9 * held_keys['alt'])) * time.dt
            self.position += camera.down * held_keys['q'] * (self.move_speed + (self.move_speed * held_keys['shift']) - (self.move_speed*.9 * held_keys['alt'])) * time.dt

            if camera.z < 0:
                camera.z += held_keys['w'] * (self.move_speed + (self.move_speed * held_keys['shift']) - (self.move_speed*.9 * held_keys['alt'])) * time.dt
            else:
                self.position += camera.forward * held_keys['w'] * (self.move_speed + (self.move_speed * held_keys['shift']) - (self.move_speed*.9 * held_keys['alt'])) * time.dt

            camera.z -= held_keys['s'] * (self.move_speed + (self.move_speed * held_keys['shift']) - (self.move_speed*.9 * held_keys['alt'])) * time.dt

        if mouse.middle:
            if not camera.orthographic:
                zoom_compensation = -camera.z * .1
            else:
                zoom_compensation = camera.orthographic * camera.fov * .2

            self.position -= camera.right * mouse.velocity[0] * self.pan_speed[0] * zoom_compensation
            self.position -= camera.up * mouse.velocity[1] * self.pan_speed[1] * zoom_compensation


        # self.gizmo.position = self.position


if __name__ == '__main__':
    # window.vsync = False
    app = Ursina()
    '''
    Simple camera for debugging.
    Hold right click and move the mouse to rotate around point.
    '''

    sky = Sky()
    e = Entity(model='cube', color=color.white, collider='box')
    e.model.colorize()

    from ursina.prefabs.first_person_controller import FirstPersonController
    from copy import copy
    # player = FirstPersonController()
    # Entity(parent=player, model='cube', color=color.orange, scale_y=2, origin_y=0)
    ground = Entity(model='plane', scale=32, texture='white_cube', texture_scale=(32,32), collider='box')
    box = Entity(model='cube', collider='box', texture='white_cube', scale=(10,2,2), position=(2,1,5), color=color.light_gray)
    ec = EditorCamera(rotation_smoothing=2, enabled=False, rotation=(30,30,0))

    rotation_info = Text(position=window.top_left)

    def update():
        rotation_info.text = str(int(ec.rotation_y)) + '\n' + str(int(ec.rotation_x))

    def input(key):
        if key == 'tab':    # press tab to toggle edit/play mode
            # player.ignore = not player.ignore
            ec.enabled = not ec.enabled

    app.run()
