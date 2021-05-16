#!/usr/bin/env python3
#import re #we use re heavily, but shouldn't import it here because the whole point is that the eval'd code will do what it needs!

#Known issues:
#There's some sort of terrible error where when one picks inapplicable separators, there's no table left sometimes, resulting in a crash. This despite the fact that inapplicable separators should simply return their argument as a list.
#If you select a known format that is inapplicable, the program will just crash. This is regretable because it doesn't give the user the chance to select something else instead without rerunning the cell. However, it's not self-evident how we should present this error to the user.
#If, say, wikitextparser is selected, and we can't import say wikitextparser, we crash. This is regretable because it doesn't give the user the chance to select something else instead without rerunning the cell. However, it's not self-evident how we should present this error to the user.
# TODO: a nice try catch with an error message as output should suffice.

try:
  import pandas
except ModuleNotFoundError as e:
  print("Pandas not found. Please install pandas on the system and try again.")
  exit()

#debug print
debug = False #True #False
def dprint(s):
  if debug: print(s)

#All these globals are messy but I don't think I can pass more info around in the callbacks :/
text = ""
format_hint = ""
row_hint = ""
col_hint = ""
#TODO: the important thing is that the code can run multiple times (currently we get a dumb error), and the below might be useful:
# ... it's not actually clear how to make the main function only return a value once all the computation is confirmed?
# ... use techniques in https://ipywidgets.readthedocs.io/en/latest/examples/Widget%20Asynchronous.html to let the code run again, instead of just using this global, side-effecty variable.

table = []

#callbacks for hint buttons
def set_format_hint(b):
  global format_hint
  format_hint = b.new
  funravel(text, format_hint, row_hint, col_hint)

def set_row_hint(b):
  global row_hint
  row_hint = b.new
  funravel(text, format_hint, row_hint, col_hint)

def set_col_hint(b):
  global col_hint
  col_hint = b.new
  funravel(text, format_hint, row_hint, col_hint)

known_format_table = [ #"alpha table" of known formats to go first. strictly sorted by priority (from least to most specific ( ≈ likely to succeed)). the option "custom format" be the default if none are detected.
  #a[0] is currently "is known format", I guess.
  #a[1] is the parsing code, which MUST result in a dataframe!
  #a[2] is the name/label/descriptor/hint
  #a[3] is the import step
  #a[4] is the col_sep, used for formating the pseudohomoiconic table
  #a[5] is the row_sep, used for formating the pseudohomoiconic table
  [True, "pandas.DataFrame(wikitextparser.parse(text).tables[0].data())", 'wikimedia table', "try: import wikitextparser\nexcept Exception as e: print('please install wikitextparser in your python environment!\\n', e)", "||", "|-"],
  [True, "pandas.read_excel(StringIO(text))",  "excel", "import pandas\nfrom io import StringIO", "", ""], # note: xls or xlsx, see also https://en.wikipedia.org/wiki/List_of_file_signatures
  [True, "pandas.read_json(text, lines=True)", "JSON", "import pandas", "…", "…"],
  [True, "pandas.read_html(text)[0]", "HTML", "import pandas", "…", "<…>"], #new in pandas 1.3.0.
  [True, "pandas.read_xml(text)", "XML", "import pandas", "…", "<…>"], #new in pandas 1.3.0.
  [True, "pandas.read_csv(StringIO(text))",    "CSV",  "import pandas\nfrom io import StringIO", ",", "⏎"], #TODO: read_csv is too greedy, as any multi-line file is technically a one-column CSV. Consider adding a check/assertion that there are actual commas in there.
  [False, "{empty: False}", "custom format", "", "", ""], #most of these are just the most convenient dummy value
]

heuristic_table = [ # a table of heuristics, the "eta table", unsorted.
  #h[0] heuristic (eta score) is just some code, which we call with the text, so please don't have side effects. Highest eta score gets to be applied.
  #h[1] evaled string(!) results in an array of the rows (or, columns). Again, no side-effects please. Tho, python strings should be immutable so risks are low.
  #h[2] is the identifier of the method, which is also the "hint" and the button label, if those are used.
  #h[3] is the literal string literal imports the h[1] code will need to work

  [lambda t: t.count("\n\n")*2000, "text.split('\\n\\n')", "Separator 2 newlines",    "" , "⏎⏎"    ], #NOTE: double escaped \n in [1] bc of eval
  [lambda t: t.count("\n")*1000,   "text.split('\\n')",    "Separator newline",     "" , "⏎"     ], #NOTE: double escaped \n in [1] bc of eval
  [lambda t: t.count("\t")*100,    "text.split('\t')",     "Separator tab",   "" , "⇥"     ],
  [lambda t: t.count("|")*50,      "text.split('|')",      "Separator |",     "" , "|"     ],
  [lambda t: t.count(",")*40,      "text.split(',')",      "Separator ,",     "" , ","     ],
  [lambda t: t.count("—")*40,      "text.split('—')",      "Separator —",     "" , "—"     ],
  [lambda t: t.count(" ")*10,      "text.split(' ')",      "Separator space", "" , "␣"     ],
  
  [lambda t: sum(map(t.count, ['{','}']))*40 , "re.split('\\{|\\}', text)", "Container {}", "import re",     "}…{"], #might redo this whole concept later #NameError: name 're' is not defined?!? #This may be a bug in python, since the import is not at the top.
  [lambda t: sum(map(t.count, ['[',']']))*40 , "re.split('\\[|\\]', text)", "Container []", "import re",     "]…["],
  [lambda t: sum(map(t.count, ['(',')']))*40 , "re.split('\\(|\\)', text)", "Container ()", "import re",     ")…("],
  [lambda t: sum(map(t.count, ['"','"']))*40 , """re.split('\\"|\\"', text)""", 'Container ""', "import re", '"…"'],
  [lambda t: sum(map(t.count, ["'","'"]))*40 , """re.split("\\'|\\'", text)""", "Container ''", "import re", "'…'"],

  [lambda t: 1, "[text]", "Do nothing", "", ""], #you can always do nothing! --laozi (attr) #must be wrapped in list for 2d table purposes
]

def clear_output():
  try:
    from IPython.display import clear_output
    clear_output()
  except:
    pass #guess we aren't in an IPython environment! Well, no need to clear the interactive display anyway, then.

def try_format(format, text):
  try:
    instructions = format[3]+"\ntable="+format[1] #the ol double-try is probably unnecessary.
    local_variables_from_exec_dict = {"text": text} #this is just how you have to do this
    dprint(instructions)
    exec(instructions, globals(), local_variables_from_exec_dict)
    table = local_variables_from_exec_dict['table']
    dprint(table)
    return not table.empty
  except Exception as e:
    dprint(e)
    return False

def funravel(text_to_parse, hint_for_known_format_rule="", hint_for_row_separator_rule="", hint_for_col_separator_rule=""):
  clear_output() #could set wait=True if that seemed interesting...

  global table
  global format_hint
  global row_hint
  global col_hint
  global text
  
  format_hint = hint_for_known_format_rule
  row_hint = hint_for_row_separator_rule
  col_hint = hint_for_col_separator_rule
  text = text_to_parse
  parser_program = "\n#You can use this python code to make similar texts into tables\n"

  row_sep = ""
  col_sep = ""

  try:
      text = open(text, "r").read()
  except Exception as e:
    if str(e).startswith("[Errno 2] No such file or directory:") or str(e).startswith("[Errno 22] Invalid argument:"):
      print("Since the text was not a valid filename, I assume it is the text to operate on.")
    else:
      print(e)
  print() #linebreak
  print("Input preview:")
  if len(text) < 1000:
    print(text)
  else:
    print(text[:998]+"...") #print a preview of the file

  #try known formats first
  format_hints = [f[2] for f in known_format_table]
  if format_hint in format_hints: #if we are passed a valid hint, 
    format = [h for h in known_format_table if h[2] == format_hint][0] # use it!
  else: 
    for format in known_format_table:
      if try_format(format, text): break #format will be left as its last value.
  if format[0]: #known format
    parser_program += format[3]+"\ntable="+format[1]
    col_sep = format[4]
    row_sep = format[5]
  else: #custom format
    #We have to detect what to parse, do one level of parse to detect the second level of parse, put the operations into the parser_program, and then exec the parser program
    #(We don't just immediately do the parse because we want to ensure the parser program output to be exactly the same as our output here.)
    #We could use eval here, instead of exec, but I wanted to have multiple lines of code to make the line(s) slightly less "scary". however, this also means the code snippet introduces more variables.
    
    hints = [row[2] for row in heuristic_table]
    if row_hint in hints: #if we are passed a valid hint, use it!
      m = [h for h in heuristic_table if h[2] == row_hint][0]
    else: 
      m = max(heuristic_table, key = lambda h: h[0](text))
    exec(m[3])
    row_sep = m[4]
    if m[3]: parser_program += (m[3]+"\n")
    parser_program += ("row_separated_text = "+m[1]+"\n")
    dprint(m[1])
    row_separated_text = eval(m[1])
    dprint(row_separated_text)
    
    #now for breaking apart columns!
    if col_hint in hints: #if we are passed a valid hint, use it!
      m2 = [h for h in heuristic_table if h[2] == col_hint][0]
    else: 
      text2 = row_separated_text[-1] # you know... this is PROBABLY a typical row.
      m2 = max(heuristic_table, key = lambda h: h[0](text2))
      col_sep = m2[4]
      if m2[3]: parser_program += (m2[3]+"\n")
      parser_program += ("table = ["+m2[1]+" for text in row_separated_text] \n")
      parser_program += ("table = pandas.DataFrame(table)")

  local_variables_from_exec_dict = {"text": text} #this is just how you have to do this
  dprint(parser_program)
  exec(parser_program, globals(), local_variables_from_exec_dict)
  table = local_variables_from_exec_dict['table']

  #ui (takes place AFTER parsing, to allow user to CORRECT)
  try:
    import ipywidgets
    #Note that we set initially selected button based on what rule is being used.
    #TODO: style buttons, give whole interaction segment a border and drop shadow.
    b = ipywidgets.ToggleButtons(options=format_hints, description="FORMAT: My best guess of the FORMAT is this, but you can chose a different one by selecting one of these buttons:", value=format[2])
    b.observe(set_format_hint, 'value') #I guess this is how you're supposed to do it.
    display(b)
    if not format[0]:
      b = ipywidgets.ToggleButtons(options=hints, description="ROW RULE: My best guess for the rule that forms ROWS is this, but you can chose a different one by selecting one of these buttons:", value=m[2])
      b.observe(set_row_hint, 'value') #I guess this is how you're supposed to do it.
      display(b)
      b = ipywidgets.ToggleButtons(options=hints, description="COLUMN RULE: My best guess for the rule that forms COLUMNS is this, but you can chose a different one by selecting one of these buttons:", value=m2[2])
      b.observe(set_col_hint, 'value')
      display(b)
    print("Output previews:")
    print_output_table(table, row_sep, col_sep, demo=True)
    #TODO: print parsing program into new Jupyter cell (we may have to overwrite it though) so the user can run it
  except Exception as e:
    #we begin with some documentation of error values, for developer use.
    #str(e)
    "No module named 'ipywidgets'"  #You need to install ipywidgets to run this program with a graphical user interface, please run `pip install ipywidgets` or equivalent in your command line or equivalent (Sorry, end user, you cannot install python packages from within python).
    "name 'display' is not defined" # I guess this is just how it looks when invoked from the command line.
    "name 'ipywidgets' is not defined" #"import ipywidgets" is missing. However, this import should have been imported by the library automatically. If you see this error, please contact the developer so he can update this error message to explain this mysterious circumstance. Maybe putting "import ipywidgets" in your program will help.')
    print()
    print("Note: While trying to display the interactive display, I encountered this error: ", e)
    print("The interactive display could not be started so you must manually pass hints to the function in python code.") #improve error message
    print("If you would like to use the interactive display please make sure you are operating in a Jupyter Notebook or similar IPython environment.") #improve error message
    print()
    print("")
    print("Output preview:")
    print_output_table(table, row_sep, col_sep, demo=False)
    print()
    print(parser_program) # we don't have any cells on the console so we just print this.

  #return table #TODO: check this assumption: as it happens we already assign to table so we shouldn't need this... I think? Maybe the assignment is local not global. Hmm. Anyway, it's a pain, because returning it tends to make the notebook print extra output (the return value), though that could be supressed.

def print_output_table(dataframe, rowsep, colsep, demo=False):
  """here we print the output table to the user, formatted appropriately with the separators.
  The way we do this is, we cheat a little, to maintain the illusion of in-place formatting."""
  if(demo):
    print("(a)")
    print(dataframe)
    print()
    print("(b)")
    print(dataframe.values.tolist())
    print()
    print("(c)")
  max_widths = {}
  for index, column in enumerate(dataframe):
    max_widths[index] = 0
    for value in dataframe[column].values:
      if max_widths[index] < len(value): max_widths[index] = len(value)
  for row in dataframe.values.tolist():
      print((" "+colsep+" ").join([v.ljust(max_widths[i]) for i, v in enumerate(row)])+rowsep)