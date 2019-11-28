from ursina import *

app = Ursina()

Button('Here is some text').fit()
Text('Make a file called "settings.py" in the root folder and \nthe engine will run the code in it.', y=.4, z=-1, origin=(0,0))

app.run()
