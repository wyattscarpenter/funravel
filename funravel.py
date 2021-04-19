#!/usr/bin/env python3

row_hint = ""
col_hint = ""

#callbacks for hint buttons
#TODO: clear display and rerun main function after doing this, and make the main function take hints accordingly.
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

#["This is "+ x for x in ['csv', 'json', 'xml', 'xls', 'wikipedia table']]+["Separator "+ x for x in ['⏎⏎', '⏎', 'tab', 'space','|']] + ["Container "+ x for x in ['{}','[]','()', '""', "''"]]
"""
hints = [
['This is csv',
['This is json',
['This is xml',
['This is xls',
['This is wikimedia table',
['Separator ⏎⏎',
['Separator ⏎',
['Separator tab',
['Separator space',
['Separator |',
['Container {}',
['Container []',
['Container ()',
['Container ""',
["Container ''",
]
"""
heuristic_table = [ # a table of heuristics, strictly sorted by priority: [test, code, description]
  #h[0] (eta score) is just some code, which we call with the text, so please don't have side effects.
  #h[1] (lamdba result) (evaled string!) results in an array of the rows (or, columns). Again, no side-effects please. Tho, python strings should be immutable so risks are low.
  #TODO: h[2] should be `hints` above. Also maybe it should be h[0] when you get right down to it?
  [lambda t: t.count("\t")*100 , "text.split('\t')", "tab?"],
  [lambda t: t.count(",")*200 , "text.split(',')", "comma"], #TODO: bug when , is lower than \t?
  [lambda t: t.count("\n\n")*2000 , "text.split('\\n\\n')", "⏎⏎"], #NOTE: double escaped \n bc of eval
  [lambda t: t.count("\n")*1000 , "text.split('\\n')", "⏎"],
  [lambda t: False, "json.loads(text)", "json"], #could this actually, uh, do anything? #also, it might do everything jsony...
  [lambda t: 1, "text", "Do Nothing"], #one can always do nothing.
]

def funravel(text, row_hint="", col_hint=""):
  global parser_program
  try:
      text = open(text, "r").read()
  except Exception as e:
    print(e)
    print("Since the text was not a valid filename, I assume it is the text to operate on:") #must improve this message
  #We have to detect what to parse, compile the operations into the parser_program, and then eval the parser program
  # We don't just literally do the parse (instead we evaluate), because we want the parser program output to be exactly the same as our output here.
  # I mean, actually we do do the parse here, but I'm not done writing the program yet...
  '''
  #this code seems to work. But we shouldn't use it because we need to use the parser_program instead
  m = max(heuristic_table, key = lambda h: h[0](text))
  #print(m[2])
  parser_program += m[1]
  row_separated_text = eval(m[1])
  text2 = row_separated_text[-1] # you know... this is PROBABLY a typical row.
  m2 = max(heuristic_table, key = lambda h: h[0](text2))
  parser_program += m[1] #TODO: need extra step
  #print(m2[2])
  table = [eval(m2[1]) for text in row_separated_text] #man... I wonder if this will work.
  #print_output_table(table)
  '''
  #ok this is the actual parser_program version.
  #we could use eval here, instead of exec, but I wanted to have multiple lines of code to make the line(s) slightly less "scary". however, this also means the code snippet introduces more variables. Exec seems to be hygenic, but that might be a problem for the end user...
  parser_program = "" #clear this in case it has any junk in it
  m = max(heuristic_table, key = lambda h: h[0](text))
  parser_program += ("row_separated_text = "+m[1]+"\n")
  row_separated_text = eval(m[1])
  text2 = row_separated_text[-1] # you know... this is PROBABLY a typical row.
  m2 = max(heuristic_table, key = lambda h: h[0](text2))
  parser_program += ("table = ["+m2[1]+" for text in row_separated_text] \n")
  print(text)
  local_variables_from_exec_dict = {"text": text} #this is just how you have to do this
  exec(parser_program, globals(), local_variables_from_exec_dict)
  table = local_variables_from_exec_dict['table']
  print_output_table(table)
  print(parser_program)
  return table

def print_output_table(table, rowsep="<", colsep="|"): #TODO: make non-optional
  """here we print the output table to the user, formatted appropriately with the separators.
  The way we do this is, we cheat a little, to maintain the illusion of in-place formatting."""
  #NOTE: just tabs and newlines thus far...
  for row in table:
      print(("\t"+colsep+" ").join(row)+"\t"+rowsep) #tabs probably won't cut it... will have to compute/format more. maybe df has builtin jazz?

def test_funravel():
  print(funravel("f"))
  print(funravel("f,v\tv"))
  print(funravel("we three kings.csv"))

test_funravel()