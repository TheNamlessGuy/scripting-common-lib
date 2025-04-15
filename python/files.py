import os

from . import print
from . import input

def cwd(*, for_path = None):
  if for_path is None:
    return os.getcwd()

  for_path = os.path.realpath(for_path)
  return for_path if not os.path.isfile(for_path) else os.path.dirname(for_path)

def validate_paths(paths, *, filled = False):
  if not isinstance(paths, list): paths = [paths]

  if filled and len(paths) == 0:
    print.fatal_error("No paths specified")

  nonexistent_paths = [x for x in paths if not os.path.exists(x)]
  if len(nonexistent_paths) > 0:
    print.fatal_error("The following paths couldn't be found:", print._format_variable(nonexistent_paths))

def listdir(path):
  return [os.path.join(path, x) for x in os.listdir(path)]

def process_files(paths, processing_function, *, _toplevel = True, autoresponse = None, is_valid = lambda x: True):
  for path in paths:
    if os.path.isfile(path):
      if not is_valid(path):
        continue
      elif _toplevel:
        confirmed = True
      else:
        print.framed(path)
        confirmed = input.confirm("Process this file?", default = True, autoresponse = autoresponse)

      if confirmed:
        processing_function(path)
    elif os.path.isdir(path):
      if _toplevel:
        confirmed = True
      else:
        print.framed(path)
        confirmed = input.confirm("Process this folder?", default = True, autoresponse = autoresponse)

      if confirmed:
        process_files(listdir(path), processing_function, _toplevel = False, autoresponse = autoresponse, is_valid = is_valid)