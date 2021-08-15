import re


class Color:
    COLORS = {
        'pink': '\033[95m',
        'blue': '\033[94m',
        'bblue': "\033[1;34m",
        'red': '\033[31m',
        'bred': "\033[1;31m",
        'green': '\033[92m',
        'bgreen': "\033[0;32m",
        'yellow': '\033[93m',
        'orange': '\033[91m',
        'gray': '\033[37m',
        'reverse': "\033[;7m",
        'bold': '\033[1m',
        'blink': '\033[5m',
        'underline': '\033[4m'
    }
    CLEAR_SCREEN = '\033[2J'
    END = '\033[0m'
    enabled = True


def enable_colors(mode):
    Color.enabled = mode


def colored(attrib, text):
    if not Color.enabled:
        return text
    if type(attrib) != list:
        attrib = [attrib]
    attrib = ''.join([Color.COLORS[a] for a in attrib])
    return attrib + str(text) + Color.END


ANSI_ESCAPE = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')


def uncolored(text):
    return ANSI_ESCAPE.sub('', text)
