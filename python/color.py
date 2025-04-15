import random

_NULL = '\033[00m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
RED = '\033[31m'
GREEN = '\033[32m'
PURPLE = '\033[35m'
CLOWN_VOMIT = 'clown vomit'

COLORS = [
  BLUE,
  YELLOW,
  RED,
  GREEN,
  PURPLE,
]

def string(msg, color):
  if color != CLOWN_VOMIT:
    return "{0}{1}{2}".format(color, msg, _NULL)

  retval = ''
  previous_color = None
  for c in msg:
    while True:
      color = random.choice(COLORS)
      if color != previous_color:
        break
    retval += '{0}{1}'.format(color, c)
    previous_color = color

  return retval + _NULL