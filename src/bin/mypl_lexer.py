"""The MyPL Lexer class.

NAME: <your name here>
DATE: Spring 2024
CLASS: CPSC 326

"""

from mypl_token import *
from mypl_error import *
import time


class Lexer:
    """For obtaining a token stream from a program."""

    def __init__(self, in_stream):
        """Create a Lexer over the given input stream.

        Args:
            in_stream -- The input stream. 

        """
        self.in_stream = in_stream
        self.line = 1
        self.column = 0


    def read(self):
        """Returns and removes one character from the input stream."""
        self.column += 1
        return self.in_stream.read_char()

    
    def peek(self):
        """Returns but doesn't remove one character from the input stream."""
        return self.in_stream.peek_char()

    
    def eof(self, ch):
        """Return true if end-of-file character"""
        return ch == ''

    
    def error(self, message, line, column):
        raise LexerError(f'{message} at line {line}, column {column}')

    
    # ints, doubles, ids, reserved words.
    def next_token(self):
        """Return the next token in the lexer's input stream."""
       
        # list of reserved words to check against
        words = ['int', 'double', 'string', 'bool', 'void', 'struct',
                  'array', 'if', 'elseif', 'else', 'new', 'return', 'and'
                  , 'or', 'not', 'null', 'true', 'false', 'while', 'for']
        types = [TokenType.INT_TYPE, TokenType.DOUBLE_TYPE, TokenType.STRING_TYPE, TokenType.BOOL_TYPE,
                 TokenType.VOID_TYPE, TokenType.STRUCT, TokenType.ARRAY, TokenType.IF, TokenType.ELSEIF,
                 TokenType.ELSE, TokenType.NEW, TokenType.RETURN, TokenType.AND, TokenType.OR, TokenType.NOT,
                 TokenType.NULL_VAL, TokenType.BOOL_VAL, TokenType.BOOL_VAL, TokenType.WHILE, TokenType.FOR]
        
        # read initial character
        ch = self.read()
        token = Token(TokenType.ID, '', 0, 0)
        
        # whitespace 
        while(ch.isspace()):
            if(ch == '\n'):
                self.line = self.line + 1
                self.column = 0
            ch = self.read()
        token.column = self.column
        token.line = self.line


        # eof
        if(self.eof(ch)):
            token.token_type = TokenType.EOS

        
            
        # single character operators
        elif(ch == '.'):
            token.lexeme = '.'
            token.token_type = TokenType.DOT
           
        elif(ch == ','):
            token.lexeme = ','
            token.token_type = TokenType.COMMA

        elif(ch == '('):
            token.lexeme = '('
            token.token_type = TokenType.LPAREN

        elif(ch == ')'):
            token.lexeme = ')'
            token.token_type = TokenType.RPAREN

        elif(ch == '['):
            token.lexeme = '['
            token.token_type = TokenType.LBRACKET
        elif(ch == ']'):
            token.lexeme = ']'
            token.token_type = TokenType.RBRACKET

        elif(ch == ';'):
            token.lexeme = ';'
            token.token_type = TokenType.SEMICOLON

        elif(ch == '{'):
            token.lexeme = '{'
            token.token_type = TokenType.LBRACE

        elif(ch == '}'):
            token.lexeme = '}'
            token.token_type = TokenType.RBRACE

        elif(ch == '+'):
            token.lexeme = '+'
            token.token_type = TokenType.PLUS

        elif(ch == '-'):
            token.lexeme = '-'
            token.token_type = TokenType.MINUS

        elif(ch == '*'):
            token.lexeme = '*'
            token.token_type = TokenType.TIMES
        
        elif(ch == '/' and self.peek() != '/'):
            token.lexeme = '/'
            token.token_type = TokenType.DIVIDE

        elif(ch == '='):
            token.lexeme = '='
            token.token_type = TokenType.ASSIGN
            if(self.peek() == '='):
                token.lexeme += '='
                token.token_type = TokenType.EQUAL
                self.read()
        
        elif(ch == '>'):
            token.lexeme = '>'
            token.token_type = TokenType.GREATER
            if(self.peek() == '='):
                token.lexeme += '='
                token.token_type = TokenType.GREATER_EQ
                self.read()
        
        elif(ch == '<'):
            token.lexeme = '<'
            token.token_type = TokenType.LESS
            if(self.peek() == '='):
                token.lexeme += '='
                token.token_type = TokenType.LESS_EQ
                self.read()
        
        elif(ch == '!' and self.peek() == '='):
            token.lexeme = '!='
            token.token_type = TokenType.NOT_EQUAL
            self.read()

    

        # strings
        elif(ch == "\""):
            # until another quote is reached
            while(self.peek() != "\""):
                char = self.read()
                # non-terminated string error
                if(char == '\n' or char == ''):
                    self.error('non-terminated string', self.line, self.column)
                token.lexeme = token.lexeme + char
                
            
            self.read()
            token.token_type = TokenType.STRING_VAL

        
        # comments
        elif(ch == "/" and self.peek() == "/"):
            token.token_type = TokenType.COMMENT
            self.read()
            while self.peek() != '\n' and self.peek() != '':
                # print('peeking at: ' + self.peek())
                token.lexeme += self.read()
            # print("lexume = " + token.lexeme)
            # print('reading char at end of block: '+ self.read())
    
            # print('end of comment block')
            

        
        # words
        elif(ch.isalpha()):
            while(self.peek().isalpha() or self.peek().isnumeric() or self.peek() == '_'):
                token.lexeme += ch
                ch = self.read()
            token.lexeme += ch
            token.token_type = TokenType.ID

            if(token.lexeme in words):
                token.token_type = types[words.index(token.lexeme)]
        
        #ints and doubles
        elif(ch.isdecimal()):                
            token.token_type = TokenType.INT_VAL
            firstDec = False # becomes true on first decimal
            while(self.peek().isdecimal() or (self.peek() == '.' and not firstDec)):
                if(ch == '.'):
                    token.token_type = TokenType.DOUBLE_VAL
                    firstDec = True
                token.lexeme += ch
                ch = self.read()
            token.lexeme += ch
            # leading zero error
            if(len(token.lexeme) > 1 and token.lexeme[1] != '.' and token.lexeme[0] == '0'):
                self.error(self.error('leading zero', self.line, self.column))
            # double with no characters after . error
            if(token.lexeme[len(token.lexeme)-1] == '.'):
                self.error('invalid double', self.line, self.column)
        
        # illegal characters error
        elif(ch == '!' or ch == '?' or ch == '#' or ch == '@' or ch == '^' or ch == '$' or ch == '%' or 
             ch == '&' or ch =='|' or ch == '~' or ch == '`' or ch == ':' or ch == '_' or ch == '\\'):
            message = 'illegal character ' + ch 
            self.error(message, self.line, self.column)
            

        return token
        
      
        
            

            
            



        # TODO: finish the rest of the next_token function
