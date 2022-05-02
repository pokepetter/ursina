from ursina import *
from collections import namedtuple
from copy import copy


class Node:
    __slots__ = ['index', 'indent_level', 'content', 'code', 'children', 'is_answer']

    def __str__(self):
        return 'Node:\n    ' + '\n    '.join([f'{e} = {getattr(self, e)}' for e in Node.__slots__])


bar_mission_solved = False
class Conversation(Entity):

    def __init__(self, **kwargs):
        super().__init__(parent=camera.ui, y=-.1)

        self.question = Button(
            parent=self,
            text_origin=(-.5,0),
            scale_x=1,
            scale_y=.1,
            model=Quad(radius=.5, aspect=1/.1),
            text='What do you want\nWhat do you want?'
            )
        self.question.text_entity.line_height = 1.25
        self.question.text_entity.position = (-.45, -.05)
        self.question.highlight_color = self.question.color
        self.more_indicator = Entity(parent=self.question, model=Circle(3), position=(.45,-.4,-.1), rotation_z=180, color=color.azure, world_scale=.5, z=-1, enabled=False)
        def toggle():
            self.more_indicator.visible = not self.more_indicator.visible
            invoke(self.more_indicator.toggle, delay=.5)

        self.more_indicator.toggle = toggle
        self.more_indicator.toggle()
        self.spacing = 4 * .02
        self.wordwrap = 65
        self.button_model = Quad(radius=.5, aspect=1/.075)

        for key, value in kwargs.items():
            setattr(self, key ,value)

        self.answer_0 = Button(parent=self, text='answer_0', y=self.question.y-self.spacing-.025, scale=(1,.075), text_origin=(-.5,0), model=copy(self.button_model))
        self.answer_1 = Button(parent=self, text='answer_1', y=self.answer_0.y-self.spacing, scale=(1,.075), text_origin=(-.5,0), model=copy(self.button_model))
        self.answer_2 = Button(parent=self, text='answer_2', y=self.answer_1.y-self.spacing, scale=(1,.075), text_origin=(-.5,0), model=copy(self.button_model))

        self.buttons = (self.answer_0, self.answer_1, self.answer_2)
        for b in self.buttons:
            b.text_entity.line_height = 1.15
            b.text_entity.position = (-.45, 0)

        self.question_appear_sequence = None
        self.button_appear_sequence = None
        self.started = False



    def ask(self, node, question_part=0):
        # print(node)
        self.current_node = node
        self.question_part = question_part
        self.question.text = node.content[question_part]
        self.question.text_entity.wordwrap = self.wordwrap
        self.more_indicator.enabled = False
        self.question_appear_sequence = self.question.text_entity.appear(delay=.1)

        for b in self.buttons:
            b.enabled = False

        answers = []
        for i, child in enumerate(node.children):
            if child.code and child.code.startswith('if'):
                a = eval(child.code[3:])
                if a:
                    print('wooooooooooooooooooo', a)
                else:
                    continue

            answers.append(child)

        # multi page question
        if len(node.content) > 1 and self.question_part < len(node.content)-1:
            if self.question_part < len(node.content): # question not finished, so don't show answer buttons
                # print('question not finished')
                self.question_appear_sequence.append(Func(setattr, self.more_indicator, 'enabled', True))
                return

        self.button_appear_sequence = Sequence()
        invoke(self.button_appear_sequence.start, delay=self.question_appear_sequence.duration)

        # print('aaaaaa', [n.content for n in node.children])
        if not node.children:
            self.buttons[0].text = '*leave*'
            self.buttons[0].on_click = Func(setattr, self, 'enabled', False)
            self.button_appear_sequence.append(Func(setattr, self.buttons[0], 'enabled', True))


        for i, child in enumerate(answers):
            self.button_appear_sequence.append(Wait(i*.15))
            self.button_appear_sequence.append(Func(setattr, self.buttons[i], 'enabled', True))
            self.buttons[i].text = child.content[0]
            self.buttons[i].text_entity.wordwrap = self.wordwrap

            def on_click(node=child):
                # print(node)
                if not node.children:
                    print('end')
                    self.enabled = False
                    return


                invoke(self.ask, node.children[0], 0, delay=.1)
                if len(node.children) > 1:
                    print('error at node:', n, '. node has multiple children, but should only have one (a question)')

            self.buttons[i].on_click = on_click



    def input(self, key):
        if key == 'left mouse down' or key == 'space' and not mouse.hovered_entity in self.buttons:
            self.next()


    def next(self):
        if not self.started:
            return

        if not self.question_appear_sequence.finished and self.question_appear_sequence.t > .1:
            self.question_appear_sequence.finish()
            if self.button_appear_sequence:
                self.button_appear_sequence.start()
            return

        if self.question_part < len(self.current_node.content)-1:
            self.ask(self.current_node, self.question_part+1)


    def start_conversation(self, conversation):
        self.conversation_nodes = self.parse_conversation(conversation)
        self.ask(self.conversation_nodes[0])
        self.started = True



    def parse_conversation(self, convo):
        convo = convo.strip()
        nodes = list()
        prev_node = None
        node_index = 0

        for i, l in enumerate(convo.split('\n')):
            if not l:
                continue

            indent_level = len(l) - len(l.lstrip())
            indent_level //= 4
            content, code = l.strip(), None
            if '(' in l:
                content, code = l.split('(')
                content = content.strip()
                code = code[:-1]
                is_answer = content.startswith('* ')
                # print('code:', codeK)

            if prev_node and prev_node.indent_level == indent_level:
                prev_node.content.append(content)
                prev_node = n
                continue

            n = Node()
            n.index = node_index
            n.indent_level = indent_level
            n.is_answer = content.startswith('* ')
            if n.is_answer:
                content = content[2:]
            n.content = [content, ]
            n.children = list()
            n.code = code
            nodes.append(n)
            prev_node = n
            node_index += 1

            # look backwards through nodes to find current node's parent
            for j in range(node_index-1, -1, -1):
                if nodes[j].indent_level == n.indent_level-1:
                    nodes[j].children.append(n)
                    break


        return nodes



if __name__ == '__main__':
    app = Ursina()

    conversation = Conversation()
    # conversation.question.model = 'quad'
    # for b in conversation.buttons:
    #     b.model = 'quad'
    bar_mission_solved = False
    convo = dedent('''
    I'm looking for my sister. Can you help me find her, please? I haven't seen her in days! Who know what could've happened!?
    I'm worried. Will you help me?
        * Yes, of course. This can be a dangerous city.
            Oh no! Do you think something happened to her?
            What should I do?!
                * She's probably fine. She can handle herself.
                    You're right. I'm still worried though.
                        * Don't worry, I'll look for her.
                * Maybe. (chaos += 1)
                    Help me look for her, please! *runs off*
        * I'm sorry, but I don't have time right now.
            A true friend wouldn't say that. (evil += 1)
        * I know where she is! (if bar_mission_solved)
            Really? Where?
                * I saw her on a ship by the docks, it looked like they were ready to set off.
                    Thank you! *runs off*
    ''')
    conversation.start_conversation(convo)
    # conversation.parse_conversation(convo)

    # def input(key):
    #     if key == 'space':
    #         conversation.start_conversation()
    # window.color = color._16
    window.size = window.fullscreen_size * .5
    Sprite('shore', z=1)
    app.run()
