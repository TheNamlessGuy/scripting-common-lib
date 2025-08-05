import sys
import datetime

from . import verbosity
from . import color

class Print(sys.modules[__name__].__class__):
  def __call__(self, *args, **kwargs):
    if 'indent' in kwargs:
      args = list(args)
      args.insert(0, ' ' * (kwargs.pop('indent', 1) - 1))
      args = tuple(args)

    print(*args, **kwargs)

  def _now_stamp(self, _color):
    now = datetime.datetime.now()
    stamp = str(now.year) + '-' + str(now.month).rjust(2, '0') + '-' + str(now.day).rjust(2, '0') + ' ' + str(now.hour).rjust(2, '0') + ':' + str(now.minute).rjust(2, '0') + ':' + str(now.second).rjust(2, '0')
    return color.string('[' + stamp + ']', _color)

  def _prefix_and_print(self, color, *args, **kwargs):
    stamp_each_line = kwargs.pop('stamp_each_line', False)
    stamp_each_line_prefix = kwargs.pop('_stamp_each_line__prefix', '')
    stamp = self._now_stamp(color)

    if not stamp_each_line:
      self(stamp, *args, **kwargs)
      return

    lines = (''.join([str(x) for x in args])).split('\n')
    for line in lines:
      self(stamp_each_line_prefix, stamp, line, **kwargs)

  def info(self, *args, **kwargs):
    self._prefix_and_print(color.BLUE, *args, **kwargs)

  def warning(self, *args, **kwargs):
    self._prefix_and_print(color.YELLOW, *args, **kwargs)

  def error(self, *args, **kwargs):
    self._prefix_and_print(color.RED, *args, **kwargs)

  def fatal_error(self, *args, **kwargs):
    self.error(*args, **kwargs)
    exit(1)

  def debug(self, *args, **kwargs):
    self._prefix_and_print(color.CLOWN_VOMIT, *args, **kwargs)

  def verbose(self, level, func, *args, **kwargs):
    if verbosity.is_verbose_enough(level):
      stamp_each_line = kwargs.get('stamp_each_line', False)
      prefix = color.string('(Verbosity {0})'.format(level), color.PURPLE)
      if not stamp_each_line:
        self(prefix, end = ' ')
      func(*args, **kwargs, _stamp_each_line__prefix = prefix)

  def _format_variable(self, v):
    if isinstance(v, str):
      return "'{0}'".format(v)
    elif isinstance(v, list):
      retval = ''
      for i in range(len(v)):
        if i > 0:
          retval += ", "
        retval += self._format_variable(v[i])
      return retval

    return str(v)

  def variable(self, v):
    self(self._format_variable(v))

  def framed(self, msg):
    self('+-' + ('-' * len(msg)) + '-+');
    self('| {0} |'.format(msg))
    self('+-' + ('-' * len(msg)) + '-+');

sys.modules[__name__].__class__ = Print
