#!/usr/bin/env python3

row_hint = ""
col_hint = ""

hints = ["This is "+ x for x in ['csv', 'json', 'xml', 'xls', 'wikipedia table']]+["Separator "+ x for x in ['⏎⏎', '⏎', 'tab', 'space','|']] + ["Container "+ x for x in ['{}','[]','()', '""', "''"]]

#callbacks for hint buttons
def set_row_hint(b):
  global row_hint
  row_hint = b.new
def set_col_hint(b):
  global col_hint
  col_hint = b.new

#ui
try:
  import ipywidgets
  #TODO: set default values
  b = ipywidgets.ToggleButtons(options=hints,description="row")
  b.observe(set_row_hint, 'value') #I guess this is how you're supposed to do it.
  display(b)
  b = ipywidgets.ToggleButtons(options=hints,description="col")
  b.observe(set_col_hint, 'value')
  display(b)
except Exception as e:
  #we begin with some documentation of error values, for developer use.
  #str(e)
  "No module named 'ipywidgets'"  #You need to install ipywidgets to run this program with a graphical user interface, please run `pip install ipywidgets` or equivalent in your command line or equivalent (Sorry, end user, you cannot install python packages from within python).
  "name 'display' is not defined" # I guess this is just how it looks when invoked from the command line.
  "name 'ipywidgets' is not defined" #"import ipywidgets" is missing. However, this import should have been imported by the library automatically. If you see this error, please contact the developer so he can update this error message to explain this mysterious circumstance. Maybe putting "import ipywidgets" in your program will help.')
  print("Note: While trying to display the interactive display, I encountered this error: ", e)
  print("The interactive display could not be started so you must manually pass hints to the function in python code.") #improve error message
  print("If you would like to use the interactive display please make sure you are operating in a Jupyter Notebook or similar IPython environment.") #improve error message


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

def print_output_table():
  pass

def test_funravel():
  print(funravel("f"))
  print(funravel("f,v\tv"))
  print(funravel("funravel.py"))

test_funravel()