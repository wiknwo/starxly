"""
This script reads in raw input from terminal and displays
it to treminal window
"""
import starxly

while True:
    text = input('starxly > ')
    tokenized_text, error = starxly.run('<stdin>', text)
    if error:
        print(error)
    else:
        print(tokenized_text)