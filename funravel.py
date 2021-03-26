#!/usr/bin/env python3

parser_program = ""

heuristic_table = [ # a table of heuristics, strictly sorted by priority: [test, code, description]
  ['"\t" in text' , "text.split('\t')", "tab?"],
  ['"," in text' , "text.split(',')", "comma"],
  ["False", "json.loads(text)", "json"], #could this actually, uh, do anything? #also, it might do everything jsony...
]

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

def test_funravel():
  print(funravel("f"))
  print(funravel("f,v\tv"))
  print(funravel("funravel.py"))

test_funravel()