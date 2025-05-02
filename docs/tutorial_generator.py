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
                comment_parts.append(''.join([l.lstrip('#').lstrip(' ') for l in comment_block]))
                comment_block = []

            if is_comment_block:
                comment_block.append(line)
            else:
                code_block.append(line)


    # print('code:', code_parts)
    # print('comments:', comment_parts)
    # print('converted:', path)
    text = f'''
[← Back, documentation.html]

### {path.stem.title().replace('_',' ')}
'''
    for i, (comment, code) in enumerate(zip(comment_parts, code_parts)):
        # text += f'## {i}\n'
        text += comment
        text += '\n```\n'
        text += code[1].rstrip()
        text += '\n```\n\n'

    text += '## Result\n'
    text += '```\n'
    text += ''.join([e[1] for e in code_parts])
    text += '\n```'

    with open(f'{path.stem}.sswg', 'w', encoding='utf-8') as text_file:
        text_file.write(text)
