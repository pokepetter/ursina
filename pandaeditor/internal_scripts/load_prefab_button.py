from pandaeditor import *

class LoadPrefabButton():

    def __init__(self):
        self.path = None

    def input(self, key):
        if key == 'left mouse down' and self.entity.hovered:
            if not self.path:
                return

            print('loaf prefjna click')
            prefab = load_prefab( os.path.basename(self.path).split('.')[0])
            try:
                prefab.editor_collider = 'box'
                prefab.collider.stash()
            except Exception e:
                print(e)

            scene.editor.entity_list.populate()
