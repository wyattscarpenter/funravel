#!/usr/bin/env python3
#import re
try:
  import pandas
except ModuleNotFoundError as e:
  print("Pandas not found. Please install pandas on the system and try again.")
  exit()

#debug print
debug = False
def dprint(s):
  if debug: print(s)

#All these globals are messy but I don't think I can pass more info around in the callbacks :/
text = ""
row_hint = ""
col_hint = ""
#TODO: it's not actually clear how to make the main function only return a value once all the computation is confirmed?
#TODO: use techniques in https://ipywidgets.readthedocs.io/en/latest/examples/Widget%20Asynchronous.html to let the code run again, instead of just using this global, side-effecty variable.
table = []

#callbacks for hint buttons
def set_row_hint(b):
  global row_hint
  row_hint = b.new
  funravel(text, row_hint, col_hint)

def set_col_hint(b):
  global col_hint
  col_hint = b.new
  funravel(text, row_hint, col_hint)

#TODO: I think it probably makes more sense, on reflection, to have an "alpha table" of known formats go first, the "this is"s, and let the option "custom format" be the default if none are detected
# unclear if I will have time to make and evaluate that change in time though. Probably not too hard to code.

heuristic_table = [ # a table of heuristics, strictly sorted by priority: [test, code, description]
  #h[0] heuristic (eta score) is just some code, which we call with the text, so please don't have side effects.
  #h[1] evaled string(!) results in an array of the rows (or, columns). Again, no side-effects please. Tho, python strings should be immutable so risks are low.
  #h[2] is the identifier of the method, which is also the "hint" and the button label, if those are used.
  #h[3] is the literal string literal imports the h[1] code will need to work

  [lambda t: t.count("\n\n")*2000, "text.split('\\n\\n')", "Separator ⏎⏎",   "" , "⏎⏎"    ], #NOTE: double escaped \n in [1] bc of eval
  [lambda t: t.count("\n")*1000,   "text.split('\\n')",    "Separator ⏎",    "" , "⏎"     ], #NOTE: double escaped \n in [1] bc of eval
  [lambda t: t.count("\t")*100,    "text.split('\t')",     "Separator tab",  "" , "tab"   ],
  [lambda t: t.count("|")*50,      "text.split('|')",      "Separator |",    "" , "|"     ],
  [lambda t: t.count(" ")*10,      "text.split(' ')",     "Separator space", "" , "space" ],
  
  [lambda t: sum(map(t.count, ['{','}']))*100 , "re.split('\\{|\\}', text)", "Container {}", "import re",     "}…{"], #might redo this whole concept later
  [lambda t: sum(map(t.count, ['[',']']))*100 , "re.split('\\[|\\]', text)", "Container []", "import re",     "]…["],
  [lambda t: sum(map(t.count, ['(',')']))*100 , "re.split('\\(|\\)', text)", "Container ()", "import re",     ")…("],
  [lambda t: sum(map(t.count, ['"','"']))*100 , """re.split('\\"|\\"', text)""", 'Container ""', "import re", '"…"'],
  [lambda t: sum(map(t.count, ["'","'"]))*100 , """re.split("\\'|\\'", text)""", "Container ''", "import re", "'…'"],

  [lambda t: t.count(",")*200+t.count("\n")*1000 , "pandas.read_csv(StringIO(text))", "This is csv", "import pandas\nfrom io import StringIO", ","], #TODO: bug when , is lower than \t? #todo: this technically reads it all in one step... but, the pandas automatic columing is good
  [lambda t: sum(map(t.count, ['{','}', ",", '"', "'"]))*70, "pandas.read_json(text, lines=True)", "This is json", "import pandas", "…"], #could this actually, uh, do anything? #also, it might do everything jsony...
  [lambda t: sum(map(t.count, ['<','>', "\\"]))*10, "re.split('\\<|\\>', text)", "This is xml", "", "<…>"], #unclear if useful. maybe capture between >< when not empty? #later versions of pandas have a read_xml that might be useful...
  [lambda t: (t.startswith("\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1")+ t.startswith("\x50\x4B"))*1000 , "pandas.read_excel(StringIO(text))", "This is excel", "import pandas\nfrom io import StringIO", ""], # note: xls or xlsx, based on https://en.wikipedia.org/wiki/List_of_file_signatures
  [lambda t: sum(map(t.count, ['{|','|}']))*10000, "wikitextparser.parse(text).tables[0].data()", 'This is wikimedia table', "try: import wikitextparser\nexcept Exception as e: print('please install wikitextparser in your python environment!\\n', e)", "||"], #TODO: just remove this if we don't have wikitextparser I guess. try to import and if not, remove [-2] from this table?

  [lambda t: 1, "[text]", "Do nothing", "", ""], #you can always do nothing! --laozi (attr) #must be wrapped in list for 2d table purposes
]

def funravel(text_to_parse, hint_for_row_separator_rule="", hint_for_col_separator_rule=""):
  global table
  global row_hint
  global col_hint
  global text

  row_hint = hint_for_row_separator_rule
  col_hint = hint_for_col_separator_rule
  text = text_to_parse

  try:
      text = open(text, "r").read()
  except Exception as e:
    print(e)
    print("Since the text was not a valid filename, I assume it is the text to operate on:") #must improve this message
  print("\n"+text)

  #We have to detect what to parse, do one level of parse to detect the second level of parse, put the operations into the parser_program, and then exec the parser program
  #(We don't just immediately do the parse because we want to ensure the parser program output to be exactly the same as our output here.)
  #We could use eval here, instead of exec, but I wanted to have multiple lines of code to make the line(s) slightly less "scary". however, this also means the code snippet introduces more variables.
  
  hints = [row[2] for row in heuristic_table]
  parser_program = ""
  #if we are passed a hint, use it!
  if row_hint in hints:
    m = [h for h in heuristic_table if h[2] == row_hint][0]
  else: 
    m = max(heuristic_table, key = lambda h: h[0](text))
  exec(m[3])
  row_sep = m[4] #TODO: hmm maybe not techincally correct if the [4] is specifically the thing between records in the same line. Well, whatever for now. Don't have good examples yet.
  col_sep = ""
  parser_program += (m[3]+"\n")
  parser_program += ("row_separated_text = "+m[1]+"\n")
  dprint(m[1])
  
  row_separated_text = eval(m[1])
  dprint(row_separated_text)
  if not m[2] in ["This is csv", "This is excel", "This is json", "This is wikimedia table"]: #abandon after first parse if we already have parsed to dataframe... the data structure pandas returns will complain mightly otherwise
    #if we are passed a hint, use it!
    if col_hint in hints:
      m2 = [h for h in heuristic_table if h[2] == col_hint][0]
    else: 
      text2 = row_separated_text[-1] # you know... this is PROBABLY a typical row.
      m2 = max(heuristic_table, key = lambda h: h[0](text2))
      col_sep = m2[4]
      parser_program += (m2[3]+"\n")
      parser_program += ("table = ["+m2[1]+" for text in row_separated_text] \n")
  else:
    parser_program += ("table = row_separated_text") #kind of unclear, must fix.
  local_variables_from_exec_dict = {"text": text} #this is just how you have to do this
  exec(parser_program, globals(), local_variables_from_exec_dict)
  table = local_variables_from_exec_dict['table']

  #ui (takes place AFTER parsing, to allow user to CORRECT)
  try:
    import ipywidgets
    #clear_output() #could set wait=True if that seemed interesting...
    #Note that we set initially selected button based on what rule is being used.
    b = ipywidgets.ToggleButtons(options=hints, description="row", value=m[2])
    b.observe(set_row_hint, 'value') #I guess this is how you're supposed to do it.
    display(b)
    b = ipywidgets.ToggleButtons(options=hints, description="col", value=m2[2])
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

  print_output_table(table, row_sep, col_sep)
  print("#You can use this python code to make similar files into tables")
  print(parser_program)
  
  return table

#TODO: post-processing option?

def print_output_table(table, rowsep="<", colsep="|"): #TODO: This is currently just dummied in with odd separators and will need refinement
  """here we print the output table to the user, formatted appropriately with the separators.
  The way we do this is, we cheat a little, to maintain the illusion of in-place formatting."""
  #NOTE: just tabs and newlines thus far...
  for row in table:
      print(("\t"+colsep+" ").join(row)+"\t"+rowsep) #tabs probably won't cut it... will have to compute/format more. maybe df has builtin jazz?

def test_funravel():
  print(funravel("f"))
  print(funravel("f,v\tv"))
  print(funravel("example data/we three kings.csv"))
  print(funravel("example data/its container time.txt"))
  print(funravel("example data/example_metadata.json"))
  print(funravel("example data/example from wikitextparser documentation.txt"))

test_funravel()