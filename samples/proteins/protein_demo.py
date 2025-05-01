from ursina import Ursina, EditorCamera, DirectionalLight
from ursina.shaders import lit_with_shadows_shader
from ursina_proteins.protein import Protein
from os import path

app = Ursina(borderless=False)

protein = Protein(
    path.join(path.dirname(__file__), "insulin.pdb"),
    shader=lit_with_shadows_shader,
)

light = DirectionalLight(position=(1000, 1000, 1000))
light.look_at(protein.atoms_entity)
EditorCamera()

app.run()