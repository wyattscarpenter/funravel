# Funravel

Funravel is a python package that facilitates turning structured text into tables (specifically, python dataframes). To use funravel, install the requirements in your environment eg by running 

`pip install -r requirements.txt`

on the command line or in a jupyter notebooks `!` shell command. 

Then, use the following code in your python program.

```
import funravel
turn_text_into_table("example.txt") #this can be either a file name or the text itself
funravel.table #this variable will hold the final result
```

If run in a Jupyter Notebook, turn_text_into_table will start an interactive display that allows the user to correct its guesses. Otherwise, it will just guess at the right thing to do.

This project was completed by Wyatt S Carpenter as part of his master's thesis at the University of Cambridge, 2020-2021.
