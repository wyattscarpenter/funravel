# Funravel

Funravel is a python package that facilitates turning structured text into tables (specifically, python dataframes). To use funravel, run the following code:

```
from funravel import turn_text_into_table
turn_text_into_table("example.txt") #this can be either a file name or the text itself
```

If run in a Jupyter Notebook, turn_text_into_table will start an interactive display that allows the user to correct its guesses. Otherwise, it will just guess at the right thing to do.

This project was completed by Wyatt S Carpenter as part of his master's thesis at the University of Cambridge, 2020-2021.
