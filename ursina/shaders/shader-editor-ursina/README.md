# Ursina Engine Shader Editor 
[![GitHub commit activity (branch)](https://img.shields.io/github/commit-activity/w/ano0002/shader-editor-ursina/main)](https://github.com/ano0002/shader-editor-ursina/pulse) [![MIT License](https://img.shields.io/github/license/ano0002/shader-editor-ursina)](https://github.com/ano0002/shader-editor-ursina/blob/main/LICENSE) [![GitHub Repo stars](https://img.shields.io/github/stars/ano0002/shader-editor-ursina?style=flat)
](https://github.com/ano0002/shader-editor-ursina/stargazers) 



## Table of Contents

- [Ursina Engine Shader Editor](#ursina-engine-shader-editor)
  - [Table of Contents](#table-of-contents)
  - [What is this?](#what-is-this)
    - [Features](#features)
  - [How do I use it?](#how-do-i-use-it)
    - [Installation](#installation)
    - [Usage](#usage)
    - [Common Issues](#common-issues)
    - [Samples](#samples)
  - [Dependencies](#dependencies)
  - [Sources](#sources)
  - [License](#license)
  - [Suport me ;)](#suport-me-)
  - [Star History](#star-history)


## What is this?

This is a shader editor for the [Ursina Engine](https://www.ursinaengine.org/). It is still in development and is not ready for use yet but feel free to try it and to modify it as you want.

### Features

- Syntax highlighting
- Autocompletion
- Uniforms extraction
- Shader preview
- Shader hot-reloading

## How do I use it?

### Installation

1. Clone this repository 
2. Run `pip install -r requirements.txt` in the root directory of the repository
3. You're done! Now just run `python main.py` to start the editor.

### Usage

Simply start the editor with `python main.py` and start coding away.
To run the shader you have to click the play button in the top-right of the editor.
To see the uniforms you added in your glsl code, go in the `Uniforms` tab in the editor (click on `Extract` if you feel like some uniforms that should appear here aren't appearing).

### Common Issues
If you click on the ursina window and can't seem to regain focus on the tkinter widgets (the code editor) just switch the file opened with the tabs at the top of the tkinter window it should fix it. 


### Samples

To test if everything is working for you just open the app and click `File>Open>Shader Project`. Then just open the [`Invert_color`](\Samples\Invert_color) folder from the [`Samples`](\Samples) directory. You should see two uniforms appear in the uniform tab of the editor. To start the shader just click the play button in the top-right of the editor and then play around with the settings to see how it works.

Any feedback is appreciated.

## Dependencies

- [customtkinter](https://customtkinter.tomschimansky.com)
- [Tkinter](https://docs.python.org/3/library/tkinter.html)
- [ursina-with-tkinter](https://github.com/ano0002/ursina_with_tkinter)
  - [ursina](https://www.ursinaengine.org/)
    - [panda3d](https://www.panda3d.org/)
  - [Pmw](https://pypi.org/project/Pmw/)
- [cupcake](https://github.com/billyeatcookies/cupcake)
  - [toml](https://pypi.org/project/toml/)
  - [pillow](https://pypi.org/project/pillow//)
  - [filetype](https://pypi.org/project/filetype/)
  - [pygments](https://pygments.org/)

## Sources
All the words for autocompletion come from :
https://github.com/euler0/sublime-glsl/blob/master/GLSL.sublime-syntax
And
https://registry.khronos.org/OpenGL-Refpages/

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=ano0002/shader-editor-ursina&type=Date)](https://github.com/ano0002/shader-editor-ursina/stargazers)

