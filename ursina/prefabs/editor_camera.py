from ursina import *

class EditorCamera(Entity):

    def __init__(self, **kwargs):
        camera.editor_position = camera.position
        super().__init__(name='editor_camera', eternal=False)

        # self.gizmo = Entity(parent=self, model='sphere', color=color.orange, scale=.025, add_to_scene_entities=False, enabled=False)

        self.rotation_speed = 200
        self.pan_speed = Vec2(5, 5)
        self.move_speed = 10
        self.zoom_speed = 1.25
        self.zoom_smoothing = 8
        self.rotate_around_mouse_hit = False

        self.smoothing_helper = Entity(add_to_scene_entities=False)
        self.rotation_smoothing = 0

        for key, value in kwargs.items():
            setattr(self, key, value)

        self.start_position = self.position
        self.perspective_fov = camera.fov
        self.orthographic_fov = camera.fov
        self.on_destroy = self.on_disable
        self.hotkeys = {'toggle_orthographic':'shift+p', 'focus':'f', 'reset_center':'shift+f'}


    def on_enable(self):
        camera.org_parent = camera.parent
        camera.org_position = camera.position
        camera.org_rotation = camera.rotation
        camera.parent = self
        camera.position = camera.editor_position
        camera.rotation = (0,0,0)
        self.target_z = camera.z
        self.target_fov = camera.fov


    def on_disable(self):
        camera.editor_position = camera.position
        camera.parent = camera.org_parent
        camera.position = camera.org_position
        camera.rotation = camera.org_rotation


    def on_destroy(self):
        destroy(self.smoothing_helper)


    def input(self, key):
        combined_key = ''.join(e+'+' for e in ('control', 'shift', 'alt') if held_keys[e] and not e == key) + key

        if combined_key == self.hotkeys['toggle_orthographic']:
            if not camera.orthographic:
                self.orthographic_fov = camera.fov
                camera.fov = self.perspective_fov
            else:
                self.perspective_fov = camera.fov
                camera.fov = self.orthographic_fov

            camera.orthographic = not camera.orthographic


        elif combined_key == self.hotkeys['reset_center']:
            self.animate_position(self.start_position, duration=.1, curve=curve.linear)

        elif combined_key == self.hotkeys['focus'] and mouse.world_point:
            self.animate_position(mouse.world_point, duration=.1, curve=curve.linear)


        elif key == 'scroll up':
            if not camera.orthographic:
                target_position = self.world_position
                # if mouse.hovered_entity and not mouse.hovered_entity.has_ancestor(camera):
                #     target_position = mouse.world_point

                self.world_position = lerp(self.world_position, target_position, self.zoom_speed * time.dt * 10)
                self.target_z += self.zoom_speed * (abs(self.target_z)*.1)
            else:
                self.target_fov -= self.zoom_speed * (abs(self.target_fov)*.1)
                self.target_fov = clamp(self.target_fov, 1, 200)

        elif key == 'scroll down':
            if not camera.orthographic:
                # camera.world_position += camera.back * self.zoom_speed * 100 * time.dt * (abs(camera.z)*.1)
                self.target_z -= self.zoom_speed * (abs(self.target_z)*.1)
            else:
                self.target_fov += self.zoom_speed * (abs(self.target_fov)*.1)
                self.target_fov = clamp(self.target_fov, 1, 200)

        elif key == 'right mouse down' or key == 'middle mouse down':
            if mouse.hovered_entity and self.rotate_around_mouse_hit:
                org_pos = camera.world_position
                self.world_position = mouse.world_point
                camera.world_position = org_pos



    def update(self):
        if mouse.right:
            self.smoothing_helper.rotation_x -= mouse.velocity[1] * self.rotation_speed
            self.smoothing_helper.rotation_y += mouse.velocity[0] * self.rotation_speed

            self.direction = Vec3(
                self.forward * (held_keys['w'] - held_keys['s'])
                + self.right * (held_keys['d'] - held_keys['a'])
                + self.up    * (held_keys['e'] - held_keys['q'])
                ).normalized()

            self.position += self.direction * (self.move_speed + (self.move_speed * held_keys['shift']) - (self.move_speed*.9 * held_keys['alt'])) * time.dt

            if self.target_z < 0:
                self.target_z += held_keys['w'] * (self.move_speed + (self.move_speed * held_keys['shift']) - (self.move_speed*.9 * held_keys['alt'])) * time.dt
            else:
                self.position += camera.forward * held_keys['w'] * (self.move_speed + (self.move_speed * held_keys['shift']) - (self.move_speed*.9 * held_keys['alt'])) * time.dt

            self.target_z -= held_keys['s'] * (self.move_speed + (self.move_speed * held_keys['shift']) - (self.move_speed*.9 * held_keys['alt'])) * time.dt

        if mouse.middle:
            if not camera.orthographic:
                zoom_compensation = -self.target_z * .1
            else:
                zoom_compensation = camera.orthographic * camera.fov * .2

            self.position -= camera.right * mouse.velocity[0] * self.pan_speed[0] * zoom_compensation
            self.position -= camera.up * mouse.velocity[1] * self.pan_speed[1] * zoom_compensation

        if not camera.orthographic:
            camera.z = lerp(camera.z, self.target_z, time.dt*self.zoom_smoothing)
        else:
            camera.fov = lerp(camera.fov, self.target_fov, time.dt*self.zoom_smoothing)

        if self.rotation_smoothing == 0:
            self.rotation = self.smoothing_helper.rotation
        else:
            self.quaternion = slerp(self.quaternion, self.smoothing_helper.quaternion, time.dt*self.rotation_smoothing)
            camera.world_rotation_z = 0


    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        if hasattr(self, 'smoothing_helper') and name in ('rotation', 'rotation_x', 'rotation_y', 'rotation_z'):
            setattr(self.smoothing_helper, name, value)



if __name__ == '__main__':
    # window.vsync = False
    app = Ursina(vsync=False)
    '''
    Simple camera for debugging.
    Hold right click and move the mouse to rotate around point.
    '''

    sky = Sky()
    e = Entity(model=load_model('cube', use_deepcopy=True), color=color.white, collider='box')
    e.model.colorize()

    from ursina.prefabs.first_person_controller import FirstPersonController

    ground = Entity(model='plane', scale=32, texture='white_cube', texture_scale=(32,32), collider='box')
    box = Entity(model='cube', collider='box', texture='white_cube', scale=(10,2,2), position=(2,1,5), color=color.light_gray)
    player = FirstPersonController(y=1, enabled=True)

    ec = EditorCamera(rotation_smoothing=3)
    ec.enabled = False
    rotation_info = Text(position=window.top_left)

    def update():
        rotation_info.text = str(int(ec.rotation_y)) + '\n' + str(int(ec.rotation_x))


    def input(key):
        if key == 'tab':    # press tab to toggle edit/play mode
            ec.enabled = not ec.enabled
            player.enabled = not player.enabled


    app.run()
