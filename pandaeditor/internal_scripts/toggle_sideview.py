from pandaeditor import *


class ToggleSideview():

    def on_click(self):
        camera_original_parent = camera.parent
        camera.reparent_to(scene.editor.editor_camera.camera_pivot)
        scene.editor.editor_camera.camera_pivot.rotation = (0,0,0)
        camera.reparent_to(camera_original_parent)
