import sys
import json

from . import print

def _is_compact(prefix, compacts, *, override):
  if override is not None:
    return override

  for compact in compacts:
    if len(compact) > len(prefix):
      continue

    is_match = True
    for i in range(len(prefix)):
      if len(compact) <= i:
        is_match = True
        break
      elif prefix[i] != compact[i]:
        is_match = False
        break

    if is_match:
      return True

  return False

def _indent(amount):
  return ' ' * amount

def _get_new_value(value, *, indent_by, current_indent, compact, prefix, force_compact):
  if isinstance(value, dict):
    return _pretty_print_dict(
      value,
      indent_by = indent_by,
      _current_indent = current_indent,
      compact = compact,
      _prefix = prefix,
      force_compact = force_compact,
    )
  elif isinstance(value, list):
    return _pretty_print_list(
      value,
      indent_by = indent_by,
      _current_indent = current_indent,
      compact = compact,
      _prefix = prefix,
      force_compact = force_compact,
    )
  elif isinstance(value, bool):
    return ["false", "true"][value]
  elif isinstance(value, int) or isinstance(value, float):
    return str(value)
  elif isinstance(value, str):
    return '"{0}"'.format(value.replace('"', '\\"'))
  else:
    print.error("Unknown value type '{0}' ({1})".format(type(value), value))
    exit(1)

def _fix_retval(retval, retval_prefix, retval_postfix, *, prefix, compact, current_indent, force_compact):
  while retval.endswith('\n'):
    retval = retval[:-1]
  while retval.endswith(','):
    retval = retval[:-1]

  indent = _indent(current_indent)

  if not _is_compact(prefix, compact, override = force_compact):
    retval_prefix = retval_prefix + '\n'
    retval_postfix = '\n' + indent + retval_postfix
  else:
    while retval.startswith(' '):
      retval = retval[1:]

  return retval_prefix + retval + retval_postfix

def _pretty_print_list(lst, *, indent_by, _current_indent, compact, _prefix, force_compact):
  if len(lst) == 0:
    return '[]'

  retval = ''

  for entry in lst:
    current_indent = _current_indent + indent_by
    indent = _indent(current_indent)

    is_compact = _is_compact(_prefix, compact, override = force_compact)
    children_are_compact = True if _is_compact(_prefix + ['*'], compact, override = force_compact) else None

    new_value = _get_new_value(
      entry,
      indent_by = indent_by,
      current_indent = current_indent,
      compact = compact,
      prefix = _prefix,
      force_compact = children_are_compact,
    )

    result = '{0},'.format(new_value)
    if is_compact:
      retval += ' ' + result
    else:
      retval += indent + result + '\n'

  return _fix_retval(
    retval,
    '[', ']',
    prefix = _prefix,
    compact = compact,
    current_indent = _current_indent,
    force_compact = force_compact,
  )

def _pretty_print_dict(obj, *, indent_by, _current_indent, compact, _prefix, force_compact):
  if len(obj) == 0:
    return '{}'

  retval = ''

  for key, value in obj.items():
    current_indent = _current_indent + indent_by
    indent = _indent(current_indent)

    prefix = _prefix + [key]
    is_compact = _is_compact(prefix, compact, override = force_compact)
    was_compact = _is_compact(prefix[:-1], compact, override = force_compact)

    new_value = _get_new_value(
      value,
      indent_by = indent_by,
      current_indent = current_indent,
      compact = compact,
      prefix = prefix,
      force_compact = force_compact,
    )

    result = '"{0}": {1},'.format(key, new_value)
    if is_compact and was_compact:
      retval += ' ' + result
    else:
      retval += indent + result + '\n'

  return _fix_retval(
    retval,
    '{', '}',
    prefix = _prefix,
    compact = compact,
    current_indent = _current_indent,
    force_compact = force_compact,
  )

def pretty_print(obj, *, indent = 2, compact = []):
  return _pretty_print_dict(
    obj,
    indent_by = indent,
    _current_indent = 0,
    compact = [x.split('.') for x in compact],
    _prefix = [],
    force_compact = None,
  )

json.pretty_print = pretty_print

sys.modules[__name__] = json
