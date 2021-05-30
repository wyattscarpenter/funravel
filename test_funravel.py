from funravel import turn_text_into_table

turn_text_into_table("f")
turn_text_into_table("f,v\tv")
turn_text_into_table("example data/we three kings.csv")
turn_text_into_table("example data/its container time.txt")
turn_text_into_table("example data/example_metadata.json")
turn_text_into_table("example data/wikimedia table example.txt")
turn_text_into_table("example data/the sign language a manual of signs 1918 by j schuyler long auxiliary verbs.txt")
turn_text_into_table("example data/the sign language a manual of signs 1918 by j schuyler long auxiliary verbs.txt", hint_for_known_format_rule="custom format", hint_for_row_separator_rule="Separator 2 newlines", hint_for_col_separator_rule="Separator —")
turn_text_into_table("example data/chinese novels from wikipedia.txt")