import sys

from . import print

class Input(sys.modules[__name__].__class__):
  def __call__(self, *args, **kwargs):
    input(*args, **kwargs)

  def choice(self, msg, *, choices, default = None, printfunc = None, autoresponse = None):
    default = default.lower() if default is not None else None
    choices = [x.lower() for x in choices]

    if not msg.endswith(' ') and not msg.endswith('\n'):
      msg += ' '

    msg += '['
    for i, choice in enumerate(choices):
      if i > 0:
        msg += '/'
      msg += choice.upper() if choice == default else choice
    msg += '] '

    if printfunc is not None:
      msg = printfunc(msg)

    if autoresponse is not None:
      if autoresponse not in choices:
        print.fatal_error("Autoresponse not part of choice list")
      print(msg + autoresponse)
      return autoresponse

    while True:
      answer = input(msg).lower()
      if len(answer) == 0 and default is not None:
        return default
      elif answer in choices:
        return answer

  def confirm(self, msg, *, default = None, printfunc = None, autoresponse = None):
    if default == True:
      default = 'y'
    elif default == False:
      default = 'n'

    if autoresponse == True:
      autoresponse = 'y'
    elif autoresponse == False:
      autoresponse = 'n'

    answer = self.choice(msg, choices = ['y', 'n'], default = default, printfunc = printfunc, autoresponse = autoresponse)
    return answer == 'y'

  def input_and_confirm(self, input_msg, *, confirm_msg = "Is '{0}' alright?", confirm_default = None, input_empty_allowed = True, confirm_printfunc = None):
    input_msg += ' '
    while True:
      response = input(input_msg)

      if len(response) == 0 and not input_empty_allowed:
        continue

      answer = self.confirm(confirm_msg.format(print.color(response, print.COLOR_BLUE)), default = confirm_default, printfunc = confirm_printfunc)
      if answer:
        return response

sys.modules[__name__].__class__ = Input