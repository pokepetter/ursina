from pathlib import Path

files = [
    Path('platformer_tutorial.py'),
    ]

for path in files:
    code_parts = []
    comment_parts = []

    with open(path, encoding='utf8') as f:
        comment_block = []
        code_block = []
        is_comment_block = False

        lines = f.readlines()
        y = 0 # track the nujmber for non-commented lines
        for i, line in enumerate(lines):
            if line.startswith('#'):
                if not is_comment_block:
                    is_comment_block = True
                elif code_block:
                    # print('--------------------end code block and add it to the list')
                    code_parts.append((y, ''.join(code_block)))
                    y += len(code_block)
                    code_block = []

            if is_comment_block and not line.startswith('#'):
                is_comment_block = False
                comment_parts.append(''.join([l.lstrip('#').lstrip() for l in comment_block]))
                comment_block = []

            if is_comment_block:
                comment_block.append(line)
            else:
            # elif i > 0 and not lines[i-1].startswith('#'):
                print('add:', line[:-1])
                code_block.append(line)
                # code_without_comments.append(line)

    # code_without_comments = ''.join(code_without_comments)

    print('code:', code_parts)
    print('comments:', comment_parts)
    print('converted:', path)
    text = f'''
[← Back, documentation.html]
# arial, normal, size 1, width 1250
# center, bold, size 4
{path.stem.title().replace('_',' ')}
# left, size 1, normal\n\n\n
'''
    for i, (comment, code) in enumerate(zip(comment_parts, code_parts)):
        # text += f'## {i}\n'
        text += comment
        text += '\n# code\n'
        text += code[1].rstrip()
        text += '\n# text\n\n'

    text += '## Result\n'
    text += '# code\n'
    text += ''.join([e[1] for e in code_parts])
    text += '\n# text'

    with open(f'{path.stem}.txt', 'w', encoding='utf-8') as text_file:
        text_file.write(text)


# # left 300
# # code
# {code_without_comments}
# # text
# '''
#
#     )
# from ursina import *
# app = Ursina()
# window.color = color._32
#
# text_parent = Entity(parent=camera.ui, position=(-.6,.25), scale=.85)
# # texts = []
# # for (line_number, content) in code_parts:
# #     print(line_number, content)
#     # texts.append(Text(content, enabled=False))
# comment = Text(scale=.85)
#
# i = 0
# def input(key):
#     global i
#     if key == 'space' and i < len(code_parts):
#         print('----------', code_parts[i][0])
#         # text.text += code_parts[i][1]
#         height = len(code_parts[i-1][1]) * Text.size * .025
#         text = Text(code_parts[i][1], parent=text_parent, y=-code_parts[i][0] * Text.size)
#         # text.y += len(code_parts[i-1][1]) * Text.size * .025
#         text_parent.animate('y',  text_parent.y + height, curve=curve.linear, delay=.25, duration=.25)
#         text.appear()
#
#         comment.text = comment_parts[i]
#
#         i += 1
#
# Sprite('ursina_wink_0000', parent=camera.ui, x=.5, y=-.4, scale=.2)

#
# app.run()
