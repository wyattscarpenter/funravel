#!/usr/bin/env python3

#got halfway through implementing the user interface here. Realized I probably wanted a ToggleButtons instead of a lot of Buttons here, not least because displaying all the Buttons naively just stacks. But I wanted to check in the code first.

row_hint = ""
col_hint = ""

hints = ["This is "+ x for x in ['csv', 'json', 'xml', 'xls', 'wikipedia table']]+["Separator "+ x for x in ['⏎⏎', '⏎', 'tab', 'space','|']] + ["Container "+ x for x in ['{}','[]','()', '""', "''"]]

#callbacks for hint buttons
def set_row_hint(b):
  global row_hint
  row_hint = b.description
def set_col_hint(b):
  global col_hint
  col_hint = b.description

#test ui
try:
  import ipywidgets
  #could factor this out but it's not obvious that would be clearer #def button(hint):
  for hint in hints:
    b = ipywidgets.Button(description=hint)
    b.on_click(set_row_hint) #"lambda cannot contain assignment" I guess
    display(b)
  for hint in hints:
    b = ipywidgets.Button(description=hint)
    b.on_click(set_col_hint) #"lambda cannot contain assignment" I guess
    display(b)
except Exception as e:
  if str(e) == "No module named 'ipywidgets'":
    print("You need to install ipywidgets to run this program with a graphical user interface, please run `pip install ipywidgets` or equivalent in your command line or equivalent (Sorry, end user, you cannot install python packages from within python).") #TODO: this message should be altered to reflect how we're probably just not in a jupyter notebook so any just go to that.
  elif str(e) == "name 'ipywidgets' is not defined":
    print('"import ipywidgets" is missing. However, this import should have been imported by the library automatically. If you see this error, please contact the developer so he can update this error message to explain this mysterious circumstance. Maybe putting "import ipywidgets" in your program will help.')
  elif str(e) == "name 'display' is not defined": # I guess this is just how it looks when invoked from the command line.
    print("Note: interactive display could not be started (presumably we're on the command line) so you must manually pass hints.") #improve error message
  else:
    print("unexpected error occured: ", e)
    print("Note: interactive display could not be started (presumably we're on the command line) so you must manually pass hints.") #improve error message

parser_program = ""

heuristic_table = [ # a table of heuristics, strictly sorted by priority: [test, code, description]
  ['"\t" in text' , "text.split('\t')", "tab?"],
  ['"," in text' , "text.split(',')", "comma"],
  ["False", "json.loads(text)", "json"], #could this actually, uh, do anything? #also, it might do everything jsony...
]

#TODO: make this just a 2d parse
def inner_parse(data):
  for text in data:
    for heuristic in heuristic_table:
      if eval(heuristic[0]):
        print(heuristic[2])
        print(heuristic[1])
        return list(map(inner_parse, eval(heuristic[1])))
  return data

def funravel(data):
  try:
    if open(data, "r").read():
      data = open(data, "r").read()
  except Exception as e:
    #print(e)
    pass
  if isinstance(data, str):
    data = [data]
  return inner_parse(data)

def print_table():
  pass

def test_funravel():
  print(funravel("f"))
  print(funravel("f,v\tv"))
  print(funravel("funravel.py"))

test_funravel()