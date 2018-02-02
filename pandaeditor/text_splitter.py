text = '''
<lime>If <default>target has more than <red>50% hp,
<default>burn the enemy for 5 * INT fire damage
for 3 turns. <yellow>Else, deal 100 damage.
Unfreezes target. Costs <blue>10 mana.
'''.strip() + '\n'

# def find_part(value):
#     # print('value:', value)
#     part = ''
#     found_tag = False
#     for i in range(len(value)):
#         if found_tag:
#             break
#         if value[i] == '\n':
#             print('split on newline at', i)
#             break
#         if value[i] == '<':
#             print('split on tag at', i)
#             tag = ''
#             for j in range(min(10, len(value))):
#                 if value[i+j+1] == '>':
#                     found_tag = True
#                     break
#                 tag += value[i+j+1]
#
#             print('tag:', tag)
#
#         part += value[i]
#
#     print('part:', part[:-1])
#     if found_tag:
#         return (part, tag)
#
#     return (part, 'no_tag')
#
# for p in range(10):
#     out_part = find_part(text)
#     print(p, out_part)
#     text = text[len(out_part[0]):]
#     # text = text[len(out_part):]

sections = list()
section = ''

i = 0
while i < len(text)-1:
    # print(text[i])
    char = text[i]
    # section = ''
    if char == '\n' and text[i+1] != '<':
        print('create line:', section)
        section = ''
        i += 1
    elif char == '<': # find tag
        tag = ''
        for j in range(len(text)-i):
            tag += text[i+j]
            if text[i+j] == '>':
                i += j+1
                break
        print('create text:', section)
        print('next color is:', tag)
        section = ''
    else:
        section += char
        i += 1

print(section)
