'''
clicker game
make a gold counter
make a button
you earn gold for every click
when you have enough gold you can unlock new nodes to automatically generate gold!
'''



from ursina import *

app = Ursina()
window.color = color._20

gold = 0
counter = Text(text='0', y=.25, z=-1, scale=2, origin=(0,0), background=True)
button = Button(text='+', color=color.azure, scale= .125)

def button_click():
    global gold
    gold += 1
    counter.text = str(gold)

    if i > 19:
        button.animate_scale(0, duration=.4)
        destroy(button, delay=.5)

button.on_click = button_click

b = Button(cost=10, x=-.2, scale=.125, color=color.dark_gray, disabled=True)
b.tooltip = Tooltip(f'<gold>Gold Generator\n<default>Earn 1 gold every second.\nCosts {b.cost} gold.')

def button_click():
    global gold
    if gold >= b.cost:
        gold -= b.cost
        counter.text = str(gold)
        b.disabled = False
        b.color = color.green
        invoke(generate_gold, 1, 1)

def generate_gold(value=1, interval=1):
    global gold
    gold += 1
    counter.text = str(gold)
    b.animate_scale(.125 * 1.1, duration=.1)
    b.animate_scale(.125, duration=.1, delay=.1)
    invoke(generate_gold, value, delay=interval)




b.on_click = button_click


app.run()
