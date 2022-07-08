"""
This source file contains all the code for the starxly
programming language which is based on BASIC.
"""
from errorindicators import indicate_error

class Error:
    """Defining our own custom error class"""
    def __init__(self, position_start, position_end, error_name, details):
        self.position_start = position_start
        self.position_end = position_end
        self.error_name = error_name
        self.details = details

    def __str__(self):
        result = '{}:{}\n'.format(self.error_name, self.details)
        result += 'File {}, Line {}\n'.format(self.position_start.filename, self.position_start.line_number)
        result += indicate_error(self.position_start.filetext, self.position_start, self.position_end)
        return result

class IllegalCharacterError(Error):
    """Defining error representing when lexer comes across character it does not support"""
    def __init__(self, position_start, position_end, details):
        super().__init__(position_start, position_end, 'Illegal Character', details)

class InvalidSyntaxError(Error):
    """Defining error representing whenever there is an error in the parsing process"""
    def __init__(self, position_start, position_end, details):
        super().__init__(position_start, position_end, 'Invalid Syntax', details)

class RunTimeError(Error):
    """Defining error representing run time error"""
    def __init__(self, position_start, position_end, details, context):
        super().__init__(position_start, position_end, 'Runtime Error', details)
        self.context = context

    def __str__(self):
        result = self.generate_traceback()
        result += '{}:{}\n'.format(self.error_name, self.details)
        result += indicate_error(self.position_start.filetext, self.position_start, self.position_end)
        return result

    def generate_traceback(self):
        result = ''
        position = self.position_start
        context = self.context
        while context:
            result += 'File {}, Line {}, in {}\n'.format(position.filename, position.line_number, context.display_name) + result
            position = context.parent_entry_position
            context = context.parent
        return 'Traceback (most recent call last):\n' + result    

class Position:
    """Class representing our current location in the starxly source file"""
    def __init__(self, index, line_number, column_number, filename, filetext):
        self.index = index
        self.line_number = line_number
        self.column_number = column_number
        self.filename = filename
        self.filetext = filetext

    def advance(self, current_character=None):
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
    TT_EOF = 'TT_EOF'
    DIGITS = '0123456789'

    def __init__(self, type, value=None, position_start=None, position_end=None):
        """Method to initialize Token object"""
        self.type = type
        self.value = value
        # Get start and end positions of token
        if position_start:
            self.position_start = position_start.copy()
            self.position_end = position_start.copy()
            self.position_end.advance()
        if position_end:
            self.position_end = position_end.copy() 

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
                tokens.append(Token(Token.TT_PLUS, position_start=self.position))
                self.advance()
            elif self.current_character == '-':
                tokens.append(Token(Token.TT_MINUS, position_start=self.position))
                self.advance()
            elif self.current_character == '*':
                tokens.append(Token(Token.TT_MUL, position_start=self.position))
                self.advance()
            elif self.current_character == '/':
                tokens.append(Token(Token.TT_DIV, position_start=self.position))
                self.advance()
            elif self.current_character == '(':
                tokens.append(Token(Token.TT_LPAREN, position_start=self.position))
                self.advance()
            elif self.current_character == ')':
                tokens.append(Token(Token.TT_RPAREN, position_start=self.position))
                self.advance()
            else:
                position_start = self.position.copy()
                illegal_character = self.current_character
                self.advance()
                return [], IllegalCharacterError(position_start, self.position, "'" + illegal_character + "'") # Empty list specifying that we have no tokens to return
        tokens.append(Token(Token.TT_EOF, position_start=self.position))
        return tokens, None # None is specifying that we are returning with no errors

    def numberize(self):
        """Converts number string into float or integer depending on whether there is a decimal point present"""
        numberstring = ''
        is_decimal_point = False # No decimal point means integer and decimal point means float
        position_start = self.position.copy()

        while self.current_character != None and self.current_character in Token.DIGITS + '.':
            if self.current_character == '.':
                if is_decimal_point:
                    break
                is_decimal_point = True
                numberstring += '.'
            else:
                numberstring += self.current_character
            self.advance()
        return Token(Token.TT_INT, int(numberstring), position_start, self.position) if not is_decimal_point else Token(Token.TT_FLOAT, float(numberstring), position_start, self.position)

class NumberNode:
    """Node in AST representing a number"""
    def __init__(self, token):
        self.token = token
        self.position_start = self.token.position_start
        self.position_end = self.token.position_end

    def __repr__(self):
        return '{}'.format(self.token)

class BinaryOperatorNode:
    """Node in AST representing binary operator"""
    def __init__(self, left_node, operator_token, right_node):
        self.left_node = left_node
        self.operator_token = operator_token
        self.right_node = right_node
        self.position_start = self.left_node.position_start
        self.position_end = self.right_node.position_end

    def __repr__(self):
        return '({}, {}, {})'.format(self.left_node, self.operator_token, self.right_node)

class UnaryOperatorNode:
    """Node in AST represtning unary operator"""
    def __init__(self, operator_token, node):
        self.operator_token = operator_token
        self.node = node
        self.position_start = self.operator_token.position_start
        self.position_end = self.node.position_end

    def __repr__(self):
        return '({}, {})'.format(self.operator_token, self.node)

class ParseResult:
    """Class to allow us to add errors to parser"""
    def __init__(self):
        self.error = None
        self.node = None

    def register(self, result):
        """"""
        if isinstance(result, ParseResult):
            if result.error:
                self.error = result.error
                return result.node
        return result

    def success(self, node):
        """"""
        self.node = node
        return self

    def failure(self, error):
        """"""
        self.error = error
        return self

    def __repr__(self):
        return '{}'.format(self.node)

class Parser:
    """
    Idea of parser is to construct an abstract syntax tree
    of the tokens created by the lexer. AST tells us which
    operations have to be performed and in what order.
    Parser figures out if the tokens match our language 
    grammar and if it does, generate an AST accordingly.

    - Factors are the most fundamental data type
    - Terms are composed of factors
    - Expressions are composed of terms and factors
    """
    def __init__(self, tokens):
        self.tokens = tokens
        self.token_index = -1
        self.current_token = None
        self.advance()

    def parse(self):
        """"""
        result = self.extract_expression()
        if not result.error and self.current_token.type != Token.TT_EOF:
            return result.failure(InvalidSyntaxError(self.current_token.position_start, self.current_token.position_end, "Expected '+', '-', '*' or '/'"))
        return result

    def advance(self):
        self.token_index += 1
        if self.token_index < len(self.tokens):
            self.current_token = self.tokens[self.token_index]
        return self.current_token
    
    def extract_factor(self):
        """
        Method to extract factor from tokens and convert it
        into a node for the AST. Factors are the most 
        fundamental elements in our grammar.
        """
        result = ParseResult()
        token = self.current_token

        if token.type == Token.TT_PLUS or token.type == Token.TT_MINUS:
            result.register(self.advance())
            factor = result.register(self.extract_factor())
            if result.error:
                return result
            return result.success(UnaryOperatorNode(token, factor.node))

        elif token.type == Token.TT_INT or token.type == Token.TT_FLOAT:
            result.register(self.advance())
            return result.success(NumberNode(token))
        
        elif token.type == Token.TT_LPAREN:
            result.register(self.advance())
            expression = result.register(self.extract_expression())
            if result.error:
                return result
            if self.current_token.type == Token.TT_RPAREN:
                result.register(self.advance())
                return result.success(expression.node)
            else:
                return result.failure(InvalidSyntaxError(self.current_token.position_start, self.current_token.position_end, "Expected ')'"))
        return result.failure(InvalidSyntaxError(token.position_start, token.position_end, 'Expected int of float'))

    def extract_term(self):
        """Terms are composed of factors"""
        return self.extract_binary_operation(self.extract_factor, (Token.TT_MUL, Token.TT_DIV))
    
    def extract_expression(self):
        """Expressions are composed of terms and factors"""
        return self.extract_binary_operation(self.extract_term, (Token.TT_PLUS, Token.TT_MINUS))

    def extract_binary_operation(self, function, operations):
        """Helper method for extract_term and extract_expression methods to extract binary operation from tokens and convert it to a BinaryOperationNode"""
        result = ParseResult()
        left = result.register(function())
        if result.error:
            return result

        while self.current_token.type in operations:
            operator_token = self.current_token
            result.register(self.advance())
            right = result.register(function())
            if result.error:
                return result
            if isinstance(left, BinaryOperatorNode):
                left = result.success(left)
            left = BinaryOperatorNode(left.node, operator_token, right.node)
        if isinstance(left, ParseResult):
            return result.success(left.node)
        return result.success(left)

class RunTimeResult:
    """Class to keep track of the current result and error if there is any"""
    def __init__(self):
        self.value = None
        self.error = None

    def register(self, result):
        if result.error:
            self.error = result.error
        return result.value

    def success(self, value):
        self.value = value
        return self
    
    def failure(self, error):
        self.error = error
        return self
    
class Number:
    """Class for storing numbers and operating on them with other numbers"""
    def __init__(self, value):
        self.value = value
        self.set_position()
        self.set_context()

    def set_position(self, position_start=None, position_end=None):
        """Sets position of number so that we can return errors exactly where they occur"""
        self.position_start = position_start
        self.position_end = position_end
        return self

    def set_context(self, context=None):
        """Sets current context of program for traceback of error origins"""
        self.context = context
        return self

    def add(self, other):
        """Adds other number to this number"""
        if isinstance(other, Number):
            return Number(self.value + other.value).set_context(self.context), None

    def subtract(self, other):
        """Subtracts other number from this number"""
        if isinstance(other, Number):
            return Number(self.value - other.value).set_context(self.context), None

    def multiply(self, other):
        """Subtracts other number from this number"""
        if isinstance(other, Number):
            return Number(self.value * other.value).set_context(self.context), None

    def divide(self, other):
        """Subtracts other number from this number"""
        if isinstance(other, Number):
            if other.value == 0:
                return None, RunTimeError(other.position_start, other.position_end, 'Division by zero', self.context)
            return Number(self.value / other.value).set_context(self.context), None

    def __repr__(self):
        return str(self.value)

class Context:
    """Class to show traceback of errors and provide more context on error origins"""
    def __init__(self, display_name, parent=None, parent_entry_position=None):
        self.display_name = display_name
        self.parent = parent
        self.parent_entry_position = parent_entry_position


class Interpreter:
    """
    The interpreter traverses through the AST, looks at the 
    different node types and determines the code to be 
    executed.
    """
    def visit(self, node, context):
        """Processes given node and visits all its cihldren"""
        method_name = 'visit_{}'.format(type(node).__name__)
        method_call = getattr(self, method_name, self.no_visit_method)
        return method_call(node, context)

    def no_visit_method(self, node, context):
        """Raises exception when visit method does not exist"""
        raise Exception('No visit_{} method defined'.format(type(node).__name__))
    
    def visit_NumberNode(self, node, context):
        print('Found number node!')
        return RunTimeResult().success(Number(node.token.value).set_context(context).set_position(node.position_start, node.position_end))

    def visit_BinaryOperatorNode(self, node, context):
        print('Found binary operator node!')
        response = RunTimeResult()
        left = response.register(self.visit(node.left_node, context))
        if response.error: 
            return response
        right = response.register(self.visit(node.right_node, context))
        if response.error:
            return response
        result = None
        if node.operator_token.type == Token.TT_PLUS:
            result, error = left.add(right)
        elif node.operator_token.type == Token.TT_MINUS:
            result, error = left.subtract(right)
        elif node.operator_token.type == Token.TT_MUL:
            result, error = left.multiply(right)
        elif node.operator_token.type == Token.TT_DIV:
            result, error = left.divide(right)
        return response.failure(error) if error else response.success(result.set_position(node.position_start, node.position_end))

    def visit_UnaryOperatorNode(self, node, context):
        print('Found unary operator node')
        response = RunTimeResult()
        number = response.register(self.visit(node.node, context))
        if response.error:
            return response
        error = None
        if node.operator_token.type == Token.TT_MINUS:
            number, error = number.multiply(Number(-1))
        return response.failure(error) if error else response.success(number.set_position(node.position_start, node.position_end))

def run(filename, text):
    """Function to run the lexer on some text"""
    # Generate tokens
    lexer = Lexer(filename, text)
    tokens, error = lexer.tokenize()
    if error:
        return None, error
    # Generate AST
    parser = Parser(tokens)
    abstract_syntax_tree = parser.parse()
    if abstract_syntax_tree.error:
        return None, abstract_syntax_tree.error
    # Run program
    interpreter = Interpreter()
    context = Context('<program>') # Defining our initial root context
    result = interpreter.visit(abstract_syntax_tree.node, context)
    # result, error
    return result.value, result.error