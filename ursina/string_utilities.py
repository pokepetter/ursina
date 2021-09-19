import re
import traceback
from textwrap import dedent


def camel_to_snake(value):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', value)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def snake_to_camel(value):
    camel = ''
    words = value.split('_')
    for w in words:
        camel += w.title()
    return camel


def multireplace(string, replacements, ignore_case=False):
    """
    Given a string and a dict, replaces occurrences of the dict keys found in the
    string, with their corresponding values. The replacements will occur in "one pass",
    i.e. there should be no clashes.
    :param str string: string to perform replacements on
    :param dict replacements: replacement dictionary {str_to_find: str_to_replace_with}
    :param bool ignore_case: whether to ignore case when looking for matches
    :rtype: str the replaced string
    """
    rep_sorted = sorted(replacements, key=lambda s: len(s[0]), reverse=True)
    rep_escaped = [re.escape(replacement) for replacement in rep_sorted]
    pattern = re.compile("|".join(rep_escaped), re.I if ignore_case else 0)
    return pattern.sub(lambda match: replacements[match.group(0)], string)

def printvar(var):
     print(traceback.extract_stack(limit=2)[0][3][9:][:-1],"=", var)

def print_info(str, *args):
    from ursina import application
    if application.print_info:
        print('info:', str, *args)

def print_warning(str, *args):
    from ursina import application
    if application.print_warnings:
        print('\033[93mwarning:', str, *args, '\033[0m')



if __name__ == '__main__':
    print(camel_to_snake('CamelToSnake'))
    print(snake_to_camel('snake_to_camel'))
    printvar('test')
