import pathlib

from ursina.mesh_importer import obj_to_ursinamesh

MATERIAL_NAME = 'Łukasz ✨'


def _open_with_cp1252_default(original_open):
    # Simulate a Windows locale where open() does not default to UTF-8.
    def open_(self, mode='r', buffering=-1, encoding=None, *args, **kwargs):
        if 'b' not in mode and encoding is None:
            encoding = 'cp1252'
        return original_open(self, mode, buffering, encoding, *args, **kwargs)
    return open_


def test_obj_with_non_ascii_material_name_gets_mtl_color(tmp_path, monkeypatch):
    # Blender writes .obj and .mtl files as UTF-8. The .mtl file is already read as UTF-8,
    # so the .obj file must be read the same way for usemtl to match newmtl.
    (tmp_path / 'cube.mtl').write_text(f'newmtl {MATERIAL_NAME}\nKd 1.0 0.0 0.0\n\n', encoding='utf-8')
    (tmp_path / 'cube.obj').write_text(
        'mtllib cube.mtl\n'
        'o cube\n'
        'v 0 0 0\n'
        'v 1 0 0\n'
        'v 0 1 0\n'
        f'usemtl {MATERIAL_NAME}\n'
        'f 1 2 3\n',
        encoding='utf-8',
    )
    monkeypatch.setattr(pathlib.Path, 'open', _open_with_cp1252_default(pathlib.Path.open))

    mesh = obj_to_ursinamesh(folder=tmp_path, name='cube', return_mesh=True)

    assert len(mesh.colors) == 3
    assert all(tuple(c) == (1, 0, 0, 1) for c in mesh.colors)

