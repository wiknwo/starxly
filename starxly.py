"""
This source file contains all the code for the starxly
programming language which is based on BASIC.
"""

class Error:
    """Defining our own custom error class"""
    def __init__(self, position_start, position_end, error_name, details):
        self.position_start = position_start
        self.position_end = position_end
        self.error_name = error_name
        self.details = details

    def __str__(self):
        return '{}:{}:File {}:Line {}'.format(self.error_name, self.details, self.position_start.filename, self.position_start.line_number)

class IllegalCharacterError(Error):
    """Defining error representing when lexer comes across character it does not support"""
    def __init__(self, position_start, position_end, details):
        super().__init__(position_start, position_end, 'Illegal Character', details)

class Position:
    """Class representing our current location in the starxly source file"""
    def __init__(self, index, line_number, column_number, filename, filetext):
        self.index = index
        self.line_number = line_number
        self.column_number = column_number
        self.filename = filename
        self.filetext = filetext

    def advance(self, current_character):
        """Moves onto next index and updates line and column number if necessary"""
        self.index += 1
        self.column_number += 1
        if current_character == '\n':
            self.line_number += 1
            self.column_number = 0
        return self

    def copy(self):
        """Returns a copy of the current position in the starxly source file"""
        return Position(self.index, self.line_number, self.column_number, self.filename, self.filetext)

class Token:
    """
    Token has a type and an optional value. Each token comes
    from a small segment of the code.
    """
    # Static (Class) Variables: Token Types
    TT_INT = 'TT_INT'
    TT_FLOAT = 'TT_FLOAT'
    TT_PLUS = 'TT_PLUS'
    TT_MINUS = 'TT_MINUS'
    TT_MUL = 'TT_MUL'
    TT_DIV = 'TT_DIV'
    TT_LPAREN = 'TT_LPAREN'
    TT_RPAREN = 'TT_RPAREN'
    DIGITS = '0123456789'

    def __init__(self, type, value=None):
        """Method to initialize Token object"""
        self.type = type
        self.value = value

    def __repr__(self):
        """Method to provide string representation of Token object. __str__ produces class name when called with list of objects, interesting..."""
        return '{}:{}'.format(self.type, self.value) if self.value else '{}'.format(self.type)

class Lexer:
    """
    Lexer will go through input character by character and
    break up the text into tokens.
    """
    def __init__(self, filename, text):
        """Initializes Lexer object"""
        self.filename = filename
        self.text = text
        self.position = Position(-1, 0, -1, self.filename, self.text)
        self.current_character = None
        self.advance()

    def advance(self):
        """Advances lexer to next character in text"""
        self.position.advance(self.current_character)
        self.current_character = self.text[self.position.index] if self.position.index < len(self.text) else None

    def tokenize(self):
        """Tokenizes text in lexer"""
        tokens = []
        while self.current_character != None:
            if self.current_character == ' ' or self.current_character == '\t':
                self.advance()
            elif self.current_character in Token.DIGITS:
                tokens.append(self.numberize())
            elif self.current_character == '+':
                tokens.append(Token(Token.TT_PLUS))
                self.advance()
            elif self.current_character == '-':
                tokens.append(Token(Token.TT_MINUS))
                self.advance()
            elif self.current_character == '*':
                tokens.append(Token(Token.TT_MUL))
                self.advance()
            elif self.current_character == '/':
                tokens.append(Token(Token.TT_DIV))
                self.advance()
            elif self.current_character == '(':
                tokens.append(Token(Token.TT_LPAREN))
                self.advance()
            elif self.current_character == ')':
                tokens.append(Token(Token.TT_RPAREN))
                self.advance()
            else:
                position_start = self.position.copy()
                illegal_character = self.current_character
                self.advance()
                return [], IllegalCharacterError(position_start, self.position, "'" + illegal_character + "'") # Empty list specifying that we have no tokens to return
        return tokens, None # None is specifying that we are returning with no errors

    def numberize(self):
        """Converts number string into float or integer depending on whether there is a decimal point present"""
        numberstring = ''
        is_decimal_point = False # No decimal point means integer and decimal point means float
        while self.current_character != None and self.current_character in Token.DIGITS + '.':
            if self.current_character == '.':
                if is_decimal_point:
                    break
                is_decimal_point = True
                numberstring += '.'
            else:
                numberstring += self.current_character
            self.advance()
        return Token(Token.TT_INT, int(numberstring)) if not is_decimal_point else Token(Token.TT_FLOAT, float(numberstring))

def run(filename, text):
    """Function to run the lexer on some text"""
    lexer = Lexer(filename, text)
    tokens, error = lexer.tokenize()
    return tokens, error
