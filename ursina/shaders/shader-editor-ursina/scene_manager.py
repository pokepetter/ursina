from ursina import *
import json,os

class SceneManager(Entity):
    def __init__(self,path):
        super().__init__()
        self.entities = {}
        self.lights = {}
        self.path = path
    
    def load_scene(self):
        print(f"Loading {self.path}")
        file_content = json.load(open(self.path))
        self.entities_settings = file_content["entities"]
        self.create_entities()
        self.light_settings = file_content["lights"]
        self.set_light()
        self.camera_settings = file_content["camera"]
        self.set_camera()
        print("Scene loaded")
    
    def create_entities(self):
        for entity in self.entities_settings:
            print(f"Creating {entity['name']}")
            material = entity["material"]
            if hasattr(color,material["color"]):
                material["color"] = getattr(color,material["color"])
            self.entities[entity["name"]] = Entity(parent=self,
                                                   model=entity["model"],
                                                   position=entity["position"],
                                                   scale=entity["scale"],
                                                   rotation=entity["rotation"],
                                                   color=material["color"],
                                                   texture=material["texture"])
        print(f"Entities created: {len(self.entities)}")
    
    def set_light(self):
        pass
    
    def set_camera(self):
        print(f"Creating camera")
        if hasattr(self, "_ed"):
            destroy(self._ed)
        self._ed = EditorCamera(position=Vec3(0),
                                rotation=self.camera_settings["rotation"])
        camera.world_position = self.camera_settings["position"]
        self._ed.target_z = camera.z
        camera.world_rotation = self.camera_settings["rotation"]
        camera.orthographic = self.camera_settings["orthographic"]
        camera.fov = self.camera_settings["fov"]
        print(f"Camera created")

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        if not os.path.exists(value):
            raise FileNotFoundError(f"The file {value} does not exist")
        if not os.path.isfile(value):
            raise ValueError(f"{value} is not a file")
        if not hasattr(self, "path") or self._path != value:
            self._path = value
            self.reset()
            self.load_scene()
    
    def reset(self):
        for entity in self.entities:
            destroy(self.entities[entity])
        self.entities = {}
        for light in self.lights:
            destroy(self.lights[light])

if __name__ == "__main__":
    def custom_print(*args,**kwargs):
        if "log" in kwargs:
            log = kwargs["log"]
            del kwargs["log"]
        else:
            log = True
        if "sep" in kwargs:
            sep = kwargs["sep"]
            del kwargs["sep"]
        else:
            sep = " "
        if "end" in kwargs:
            end = kwargs["end"]
            del kwargs["end"]
        else:
            end = "\n"
        text = sep.join([repr(x) if not isinstance(x,str) else x for x in args])
        for key in kwargs:
            text += f"{key}={repr(kwargs[key])}"+sep
        if kwargs:
            text = text[0:-len(sep)]
        print(text,end=end)

    app = Ursina()
    scene = SceneManager("./Scenes/default.json")
    def input(key):
        if key == "space":
            scene.path = "./Scenes/scene2.json"
        if key=="i":
            custom_print(cam_pos = round(camera.world_position,2), cam_rot = round(camera.world_rotation,2), cam_fov = round(camera.fov,2),sep="\n")
    app.run()