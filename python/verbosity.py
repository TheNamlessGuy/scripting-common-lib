_VERBOSITY = 0

def is_verbose_enough(value):
  global _VERBOSITY
  return _VERBOSITY >= value

def is_verbose_flag(flag):
  return flag.startswith('-v') and all(x == 'v' for x in flag[1:])

def set_verbosity_from_flag(flag):
  global _VERBOSITY
  _VERBOSITY += (len(flag) - 1)