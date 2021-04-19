#!/usr/bin/env python3
#import re

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

heuristic_table = [ # a table of heuristics, strictly sorted by priority: [test, code, description]
  #h[0] heuristic (eta score) is just some code, which we call with the text, so please don't have side effects.
  #h[1] evaled string(!) results in an array of the rows (or, columns). Again, no side-effects please. Tho, python strings should be immutable so risks are low.
  #h[2] is the identifier of the method, which is also the "hint" and the button label, if those are used.
  #h[3] is the literal string literal imports the h[1] code will need to work

  [lambda t: t.count("\n\n")*2000, "text.split('\\n\\n')", "Separator ⏎⏎",   "" ], #NOTE: double escaped \n in [1] bc of eval
  [lambda t: t.count("\n")*1000,   "text.split('\\n')",    "Separator ⏎",    "" ], #NOTE: double escaped \n in [1] bc of eval
  [lambda t: t.count("\t")*100,    "text.split('\t')",     "Separator tab",  "" ],
  [lambda t: t.count("|")*50,      "text.split('|')",      "Separator |",    "" ],
  [lambda t: t.count(" ")*10,      "text.split(' ')",     "Separator space", "" ],
  
  [lambda t: sum(map(t.count, ['{','}']))*100 , "re.split('\\{|\\}', text)", "Container {}", "import re"], #might redo this whole concept later
  [lambda t: sum(map(t.count, ['[',']']))*100 , "re.split('\\[|\\]', text)", "Container []", "import re"],
  [lambda t: sum(map(t.count, ['(',')']))*100 , "re.split('\\(|\\)', text)", "Container ()", "import re"],
  [lambda t: sum(map(t.count, ['"','"']))*100 , """re.split('\\"|\\"', text)""", 'Container ""', "import re"],
  [lambda t: sum(map(t.count, ["'","'"]))*100 , """re.split("\\'|\\'", text)""", "Container ''", "import re"],

  [lambda t: t.count(",")*200 , "text.split(',')", "This is csv", ""], #TODO: bug when , is lower than \t? #todo: rfc-compliance
  [lambda t: False, "json.loads(text)", "This is json", ""], #could this actually, uh, do anything? #also, it might do everything jsony...
  [lambda t: False, "json.loads(text)", "This is xml", ""],
  [lambda t: False, "json.loads(text)", 'This is xls', ""],
  [lambda t: False, "json.loads(text)", 'This is wikimedia table', ""],

  [lambda t: 1, "[text]", "Do nothing", ""], #you can always do nothing! --laozi (attr) #must be wrapped in list for 2d table purposes
]

def funravel(text, row_hint="", col_hint=""):
  global parser_program
  try:
      text = open(text, "r").read()
  except Exception as e:
    print(e)
    print("Since the text was not a valid filename, I assume it is the text to operate on:") #must improve this message
  print("\n"+text)

  #We have to detect what to parse, do one level of parse to detect the second level of parse, put the operations into the parser_program, and then exec the parser program
  #(We don't just immediately do the parse because we want to ensure the parser program output to be exactly the same as our output here.)
  #We could use eval here, instead of exec, but I wanted to have multiple lines of code to make the line(s) slightly less "scary". however, this also means the code snippet introduces more variables. Exec seems to be hygenic, but that might be a problem for the end user...
  
  parser_program = ""
  m = max(heuristic_table, key = lambda h: h[0](text))
  exec(m[3])
  parser_program += (m[3]+"\n")
  parser_program += ("row_separated_text = "+m[1]+"\n")
  print(m[1])
  row_separated_text = eval(m[1])
  print(row_separated_text)
  text2 = row_separated_text[-1] # you know... this is PROBABLY a typical row.
  m2 = max(heuristic_table, key = lambda h: h[0](text2))
  parser_program += (m2[3]+"\n")
  parser_program += ("table = ["+m2[1]+" for text in row_separated_text] \n")
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
  print(funravel("its container time.txt"))

test_funravel()