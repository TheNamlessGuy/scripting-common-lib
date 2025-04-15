import sys
import numbers

from .dot_dict import DotDict
from . import print
from . import color

# Flags format:
# DotDict({
#    name: string,
#    flags?: string[],
#    description?: string,
#    value?: string[]|boolean - Defaults to True
#    default?: any - Defaults to False if value is a boolean, else None
#    catch_all?: True - Becomes a list of the non-flag elements not taken by the rest
#    help?: True - Whether or not this flag is a help flag
# })

def _error(what, value, code = 1):
  print.error("Unknown {0} '{1}'".format(what, value))
  exit(1)

def parse(flags, stop_parsing_flag = None, stop_parsing_name = 'stop_parsing'):
  retval = DotDict()

  help_flag = None
  catch_all_flag = None
  i = 0
  while i < len(flags):
    if 'catch_all' in flags[i]:
      catch_all_flag = flags[i]
    elif 'help' in flags[i]:
      help_flag = flags[i]
      flags.pop(i)
      i -= 1

    i += 1

  if help_flag is None: help_flag = DotDict({})
  if 'name' in help_flag: help_flag.pop('name')
  if 'flags' not in help_flag: help_flag.flags = ['-h', '--help']
  if 'description' not in help_flag: help_flag.description = 'Show this text'
  if 'value' not in help_flag: help_flag.value = True

  args = sys.argv[1:]
  i = 0
  # Break -abc into -a -b -c
  while i < len(args):
    if args[i].startswith('-') and not args[i].startswith('--') and len(args[i]) > 2:
      tmp = ['-{0}'.format(x) for x in list(args[i][1:])]
      args[i] = tmp[0]
      for f in tmp:
        i += 1
        args.insert(i, f)
    i += 1

  stop_parsing_mode = False
  length = len(args)
  i = 0
  while i < length:
    arg = args[i]

    if not stop_parsing_mode and arg == stop_parsing_flag:
      stop_parsing_mode = True
      i += 1
      continue
    elif stop_parsing_mode:
      if stop_parsing_name not in retval:
        retval[stop_parsing_name] = [arg]
      else:
        retval[stop_parsing_name].append(arg)
      i += 1
      continue

    found = False
    if arg in help_flag.flags:
      show_help(flags)
      exit(0)

    for flag in flags:
      if 'flags' not in flag:
        continue

      for f in flag.flags:
        if f == arg:
          found = True
          value = True if 'value' not in flag else flag.value
          if isinstance(value, bool):
            retval[flag.name] = value
          elif isinstance(value, list):
            if flag.name not in retval: retval[flag.name] = []
            for j in range(len(value)):
              i += 1
              retval[flag.name].append(args[i])

    if not found:
      if arg.startswith('-'):
        _error('flag', arg)
      elif catch_all_flag is None:
        _error('value', arg)
      elif catch_all_flag.name not in retval:
        retval[catch_all_flag.name] = [arg]
      else:
        retval[catch_all_flag.name].append(arg)

    i += 1

  for flag in flags:
    default = None
    if 'default' in flag:
      default = flag.default
    elif 'catch_all' in flag:
      default = []
    elif 'value' in flag:
      if isinstance(flag.value, bool):
        default = False
      else:
        default = None
    else:
      default = False

    if flag.name not in retval:
      retval[flag.name] = default

  return retval

def show_help(flags):
  print('Available flags:')

  parsed = []
  longest = 0
  for flag in flags:
    tmp = ['', '', flag.description]
    if 'catch_all' in flag:
      tmp[1] = '*'
      tmp[0] = color.string('*', color.BLUE)
    else:
      for f in flag.flags:
        if len(tmp[0]) == 0:
          tmp[1] = f
          tmp[0] = color.string(f, color.GREEN)
        else:
          tmp[1] += ", {0}".format(f)
          tmp[0] += ", {0}".format(color.string(f, color.GREEN))

      if 'value' in flag and isinstance(flag.value, list):
        for value in flag.value:
          tmp[1] += " <{0}>".format(value)
          tmp[0] += " {0}".format(color.string("<{0}>".format(value), color.PURPLE))

      if 'default' in flag:
        tmp[1] += " [Default: {0}]".format(print._format_variable(flag.default))
        tmp[0] += color.string(" [Default: {0}]".format(print._format_variable(flag.default)), color.YELLOW)

    parsed.append(tmp)
    if len(tmp[1]) > longest:
      longest = len(tmp[1])

  longest += 4 # Just to give some space between description and flags
  for tmp in parsed:
    while len(tmp[1]) < longest:
      tmp[1] += ' '
      tmp[0] += ' '

    print('', tmp[0], tmp[2])