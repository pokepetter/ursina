import argparse
from PIL import Image
import os


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('image_path')
    parser.add_argument('char_width')
    parser.add_argument('char_height')
    parser.add_argument('output_folder')

    args = parser.parse_args()

    dir = os.path.realpath('')
    image = Image.open(os.path.join(dir, args.image_path))
    image_width, image_height = image.size

    chars_string = ("""                                """
                """ !"#$%&'()*+,-./0123456789:;<=>?"""
                """@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_"""
                """´abcdefghijklmnopqrstuvwxyz{|}~ """)
    # chars_string = """ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890=?+!@#$%^&*()~`_{}[]<>|\:;"',-./"""
    char_names = tuple(char for char in chars_string)
    char_height = int(args.char_height)
    char_width = int(args.char_width)

    i = 0
    for y in range(int(image_height / char_height)):
        for x in range(int(image_width / char_width)):
            # print(char_names[i], x * char_width, y * char_height)
            if char_names[i] is not ' ' or i > len(chars_string):
                rect = (x * char_width,
                        y * char_height,
                        (x * char_width) + char_width,
                        (y * char_height) + char_height)
                cropped_image = image.crop(rect)
                try:
                    save_name = '_' + char_names[i]
                    if save_name.isupper():
                        save_name += 'u'
                    cropped_image.save(os.path.join(dir, args.output_folder, save_name + '.png'))
                    print(save_name + '.png')
                except:
                    pass
            i += 1

    print('Saved character sprites to:', os.path.join(dir, args.output_folder))
