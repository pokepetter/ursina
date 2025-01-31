import os
import json
import re
# from ProjectSavingEncoder import ProjectSavingEncoder

def ProjectExporter(ProjectName,ProjectPath,ToSavePath,Demo = False):
    #Loading the items
    if not os.path.exists(f"{ToSavePath}/{ProjectName}"):
        os.makedirs(f"{ToSavePath}/{ProjectName}")


    with open(f"{ProjectPath}/{ProjectName}/World items.txt","r") as WorldItemsFile:
        WorldItems = json.load(WorldItemsFile)

    with open(f"{ProjectPath}/{ProjectName}/To import.txt","r") as ToImportFile:
        ToImport = json.load(ToImportFile)

    # with open(f"{ProjectPath}/{ProjectName}/User defined functions.txt","r") as UdFuncFile:
    #     UdFunc = json.load(UdFuncFile)

    # with open(f"{ProjectPath}/{ProjectName}/User defined src.txt","r") as UdSrcFile:
    #     UdSrc = json.load(UdSrcFile)

    # with open(f"{ProjectPath}/{ProjectName}/User defined vars.txt","r") as UdVarsFile:
    #     UdVars = json.load(UdVarsFile)

    # with open(f"{ProjectPath}/{ProjectName}/Window config.txt","r") as WindowConfigFile:
    #     WindowConfig = json.load(WindowConfigFile)

    #Making a .py file

    FinalFile = ''''''
    TabIndent = "  "
    Indent = "      "
    for i in range(len(ToImport)):
        FinalFile += f"{ToImport[i]}\n"

    FinalFile += "\n"

    FinalFile += "class Game:\n"
    FinalFile += f"{TabIndent}def __init__(self):\n"

    # WorldItems = [{"cls": "Entity", "args": "(parent=scene, name=\'item_0\', enabled=True, eternal=False, position=Vec3(0, 0.6, 0), rotation=Vec3(0, 0, 0), scale=Vec3(1, 1, 1), model=\'cube\', origin=Vec3(0, 0, 0), shader=None, texture=\'white_cube\', color=color.white, collider=\'mesh\', )"}, {"cls": "Button", "args": "(parent=scene, name=\'item_1\', enabled=True, eternal=False, position=Vec3(-1.11, 0, 0), rotation=Vec3(0, 0, 0), scale=Vec3(1, 1, 1), model=\'cube\', origin=Vec3(0, 0, 0), shader=None, texture=\'white_cube\', color=color.green, )"}, {"cls": "InputField", "args": "(parent=scene, name=\'item_2\', enabled=True, eternal=False, position=Vec3(0, 1.73, 0), rotation=Vec3(0, 0, 0), scale=Vec3(1, 1, 1), model=\'cube\', origin=Vec3(0, 0, 0), shader=None, texture=\'white_cube\', color=color.green, )"}, {"cls": "Button", "args": "(parent=scene, name=\'item_3\', enabled=True, eternal=False, position=Vec3(0.06, -0.72, 0), rotation=Vec3(0, 0, 0), scale=Vec3(1, 1, 1), model=\'cube\', origin=Vec3(0, 0, 0), shader=None, texture=\'white_cube\', color=color.green, )"}, {"cls": "Entity", "args": "(parent=scene, name=\'item_4\', enabled=True, eternal=False, position=Vec3(1.09, 0, 0), rotation=Vec3(0, 0, 0), scale=Vec3(1, 1, 1), model=\'cube\', origin=Vec3(0, 0, 0), shader=None, texture=\'white_cube\', color=color.white, collider=\'mesh\', )"}]
    # names = [re.search(r"name='([^']*)'", item).group(1) for item in ]

    for item in WorldItems:
        name = re.search(r"name='([^']*)'", item['args']).group(1)
        FinalFile += f'{Indent}self.{name} = {item["cls"] + item["args"]}\n'
    if not Demo:
        FinalFile += "if __name__ == '__main__':\n    app = Ursina()\n    application.development_mode = False\n    Sky()\n    Game()\n    render.setAntialias(AntialiasAttrib.MAuto)\n    EditorCamera()\n    app.run()"
    else:
        FinalFile += "if __name__ == '__main__':\n    app = Ursina()\n    window.center_on_screen()\n    application.development_mode = False\n    window.borderless = False\n    window.size = (960,540)\n    window.exit_button.disable()\n    Sky()\n    Game()\n    render.setAntialias(AntialiasAttrib.MAuto)\n    EditorCamera()\n    app.run()"

    with open(f"{ToSavePath}/{ProjectName}/Main.py","w") as File:
        File.write(FinalFile)

    return True

if __name__ == "__main__":
    from GamePlusEditor.OtherStuff import CurrentFolderNameReturner
    
    ProjectExporter("w",f"{CurrentFolderNameReturner()}/Current Games",ToSavePath=CurrentFolderNameReturner().replace("Editor","FInal"))
