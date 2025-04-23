"""MyPL simple syntax checker (parser) implementation.

NAME: <Ryan St. Mary>
DATE: Spring 2024
CLASS: CPSC 326
"""

from mypl_error import *
from mypl_token import *
from mypl_lexer import *


class SimpleParser:

    def __init__(self, lexer):
        """Create a MyPL syntax checker (parser). 
        
        Args:
            lexer -- The lexer to use in the parser.

        """
        self.lexer = lexer
        self.curr_token = None

        
    def parse(self):
        """Start the parser."""
        self.advance()
        while not self.match(TokenType.EOS):
            if self.match(TokenType.STRUCT):
                self.struct_def()
            else:
                self.fun_def()
        self.eat(TokenType.EOS, 'expecting EOF')

        
    #----------------------------------------------------------------------
    # Helper functions
    #----------------------------------------------------------------------

    def error(self, message):
        """Raises a formatted parser error.

        Args:
            message -- The basic message (expectation)

        """
        lexeme = self.curr_token.lexeme
        line = self.curr_token.line
        column = self.curr_token.column
        err_msg = f'{message} found "{lexeme}" at line {line}, column {column}'
        raise ParserError(err_msg)


    def advance(self):
        """Moves to the next token of the lexer."""
        self.curr_token = self.lexer.next_token()
        # skip comments
        while self.match(TokenType.COMMENT):
            self.curr_token = self.lexer.next_token()

            
    def match(self, token_type):
        """True if the current token type matches the given one.

        Args:
            token_type -- The token type to match on.

        """
        return self.curr_token.token_type == token_type

    
    def match_any(self, token_types):
        """True if current token type matches on of the given ones.

        Args:
            token_types -- Collection of token types to check against.

        """
        for token_type in token_types:
            if self.match(token_type):
                return True
        return False

    
    def eat(self, token_type, message):
        """Advances to next token if current tokey type matches given one,
        otherwise produces and error with the given message.

        Args: 
            token_type -- The totken type to match on.
            message -- Error message if types don't match.

        """
        if not self.match(token_type):
            self.error(message)
        self.advance()

        
    def is_bin_op(self):
        """Returns true if the current token is a binary operation token."""
        ts = [TokenType.PLUS, TokenType.MINUS, TokenType.TIMES, TokenType.DIVIDE,
              TokenType.AND, TokenType.OR, TokenType.EQUAL, TokenType.LESS,
              TokenType.GREATER, TokenType.LESS_EQ, TokenType.GREATER_EQ,
              TokenType.NOT_EQUAL]
        return self.match_any(ts)

    
    #----------------------------------------------------------------------
    # Recursive descent functions
    #----------------------------------------------------------------------
        
    def struct_def(self):
        
        """Check for well-formed struct definition."""
        self.eat(TokenType.STRUCT, 'expecting struct')
        self.eat(TokenType.ID, 'expecting ID')
        self.eat(TokenType.LBRACE, 'expecting left brace')
        self.fields()
        self.eat(TokenType.RBRACE, 'expecting right brace')

       
        # TODO
        
    def fields(self):
        
        """Check for well-formed struct fields."""
        """ <data_type> ID ( SEMICOLON <data_type> ID )* | ϵ
"""
        types = [TokenType.INT_TYPE, TokenType.BOOL_TYPE, TokenType.VOID_TYPE, 
                 TokenType.DOUBLE_TYPE, TokenType.STRING_TYPE]
        
        while not self.match(TokenType.RBRACE):
            self.data_type()
            self.eat(TokenType.ID, 'expecting ID')
            self.eat(TokenType.SEMICOLON, 'expecting semicolon')
       
        # TODO
            
    def fun_def(self):
        
        """Check for well-formed function definition."""
        """<fun_def> ::= ( <data_type> | VOID_TYPE ) ID LPAREN <params> RPAREN LBRACE ( <stmt> )∗ RBRACE"""
        self.data_type()
        self.eat(TokenType.ID, 'expecting functon name of ID type')
        self.eat(TokenType.LPAREN, 'expecting left paren')
        self.params()
        self.eat(TokenType.RPAREN, 'expected right paren')
        self.eat(TokenType.LBRACE, 'expected left brace')
        while not self.match(TokenType.RBRACE):
            self.stmt()
        self.eat(TokenType.RBRACE, 'expected right brace')
        
        # TODO

    def params(self):
        """Check for well-formed function formal parameters."""
        
        while not self.match(TokenType.RPAREN):
            self.data_type()
            self.eat(TokenType.ID, 'expecting paramater name of type ID ')
            if not self.match(TokenType.RPAREN):
                self.eat(TokenType.COMMA, 'expecting comma')
                if(self.match(TokenType.RPAREN)):
                    self.error('extra comma')
        # TODO
    def data_type(self):
        
        """ # <data_type> ::= <base_type> | ID | ARRAY ( <base_type> | ID )"""
        if(self.match(TokenType.ID)):
            self.advance()
        elif (self.match(TokenType.ARRAY)):
            self.advance()
            if(self.match(TokenType.ID)):
                self.advance()
            else:
                self.base_type()
        else:
            self.base_type()
   
    def base_type(self):
        
        """ # <base_type> ::= INT_TYPE | DOUBLE_TYPE | BOOL_TYPE | STRING_TYPE"""
        types = [TokenType.INT_TYPE, TokenType.BOOL_TYPE, TokenType.VOID_TYPE, 
                 TokenType.DOUBLE_TYPE, TokenType.STRING_TYPE]
        if(self.match_any(types)):
            self.advance()
        else:
            self.error('expected base type')
        
    def stmt(self):
        
        """<while_stmt> | <if_stmt> | <for_stmt> | <return_stmt> SEMICOLON |
        <vdecl_stmt> SEMICOLON | <assign_stmt> SEMICOLON | <call_expr> SEMICOLON"""
        if(self.match(TokenType.WHILE)):
            self.while_stmt()
        elif(self.match(TokenType.IF)):
            self.if_stmt()
        elif(self.match(TokenType.FOR)):
            self.for_stmt()
        elif(self.match(TokenType.RETURN)):
            self.return_stmt()
            self.eat(TokenType.SEMICOLON, 'expecting semicolon')
        elif(self.match(TokenType.ID)):
            self.advance()
            if(self.match(TokenType.LPAREN)):
                self.call_expr()
                self.eat(TokenType.SEMICOLON, 'expected semicolon')
            elif(self.match(TokenType.LBRACKET) or self.match(TokenType.DOT) or self.match(TokenType.ASSIGN)):
                self.assign_stmt()
                self.eat(TokenType.SEMICOLON, 'expected semicolon')
            else:
                self.vdecl_stmt(True)
                self.eat(TokenType.SEMICOLON, 'expected semicolon')
        else:
            self.vdecl_stmt(False)
            self.eat(TokenType.SEMICOLON, 'expected semicolon')
            
            


    
    def while_stmt(self):
        
        """ WHILE LPAREN <expr> RPAREN LBRACE ( <stmt> )∗ RBRACE"""
        self.eat(TokenType.WHILE, "expected while")
        self.eat(TokenType.LPAREN, 'expected l paren')
        self.expr()
        self.eat(TokenType.RPAREN, 'expected r paren')
        self.eat(TokenType.LBRACE, 'expected l brace')
        while(not self.match(TokenType.RBRACE)):
            self.stmt()
        self.eat(TokenType.RBRACE, 'expecting RBRACE')
        


    def if_stmt(self):
        
        """IF LPAREN <expr> RPAREN LBRACE ( <stmt> )∗ RBRACE <if_stmt_t>"""
        self.eat(TokenType.IF, 'expecting IF')# eats if
        self.eat(TokenType.LPAREN, 'expecting LPAREN')
        self.expr()
        self.eat(TokenType.RPAREN, 'expecting RPAREN')
        self.eat(TokenType.LBRACE, 'expecting LBRACE')
        while not self.match(TokenType.RBRACE):
            self.stmt()
        self.eat(TokenType.RBRACE, 'expecting RBRACE')
        self.if_stmt_t()


    def if_stmt_t(self):
        
        """ELSEIF LPAREN <expr> RPAREN LBRACE ( <stmt> )∗ RBRACE <if_stmt_t> | ELSE LBRACE ( <stmt> )∗ RBRACE | ϵ"""
        if self.match(TokenType.ELSEIF):
            self.advance()
            self.eat(TokenType.LPAREN, 'expecting LPAREN')
            self.expr()
            self.eat(TokenType.RPAREN, 'expecting RPAREN')
            self.eat(TokenType.LBRACE, 'expecting LBRACE')
            while not self.match(TokenType.RBRACE):
                self.stmt()
            self.eat(TokenType.RBRACE, 'expecting RBRACE')
            self.if_stmt_t()
        elif self.match(TokenType.ELSE):
            self.advance()
            self.eat(TokenType.LBRACE, 'expecting LBRACE')
            while not self.match(TokenType.RBRACE):
                self.stmt()
            self.eat(TokenType.RBRACE, 'expecting RBRACE')
        


    def for_stmt(self):
       
        """FOR LPAREN <vdecl_stmt> SEMICOLON <expr> SEMICOLON <assign_stmt> <RPAREN> LBRACE ( <stmt> )∗ RBRACE"""
        self.eat(TokenType.FOR, 'expecting for') # eats for
        self.eat(TokenType.LPAREN, 'expected LPAREN')
        self.vdecl_stmt(False)
        self.eat(TokenType.SEMICOLON, 'expected SEMICOLON')
        self.expr()
        self.eat(TokenType.SEMICOLON, 'expected SEMICOLON')
        self.eat(TokenType.ID, 'expecting ID') # as a part of the assign_stmt grammar
        self.assign_stmt()
        self.eat(TokenType.RPAREN, 'expected RPAREN')
        self.eat(TokenType.LBRACE, 'expected LBRACE')
        while not self.match(TokenType.RBRACE):
                self.stmt()
        self.eat(TokenType.RBRACE, 'expected RBRACE')

    
    def return_stmt(self):
       
        """RETURN <expr> SEMICOLON"""
        self.eat(TokenType.RETURN, 'expecting return')
        self.expr()
        # self.eat(TokenType.SEMICOLON, 'expecting semicolon')

    def lvalue(self):
        
        """ ID ( LBRACKET <expr> RBRACKET | ϵ ) ( DOT ID ( LBRACKET <expr> RBRACKET | ϵ ) )∗"""
        """ID already eaten"""
        if(self.match(TokenType.LBRACKET)):
            self.advance()
            self.expr()
            self.eat(TokenType.RBRACKET, 'expecting RBRACKET')
        while(self.match(TokenType.DOT)):
            self.advance()
            self.eat(TokenType.ID, 'expecting ID')
            if(self.match(TokenType.LBRACKET)):
                self.advance()
                self.expr()
                self.eat(TokenType.RBRACKET, 'expecting RBRACKET')
       
        
    
    def vdecl_stmt(self, ifIdRead):
        
        """<data_type> ID ( ASSIGN <expr> | ϵ )"""
        """ID already read when called"""

        if not ifIdRead:
            self.data_type()
        self.eat(TokenType.ID, 'expected ID')
        if not self.match(TokenType.SEMICOLON):
            self.eat(TokenType.ASSIGN, 'expected =')
            self.expr()
        
    
    def assign_stmt (self):
       
        """<lvalue> ASSIGN <expr>"""
        """ID already read when called"""
        self.lvalue()
        self.eat(TokenType.ASSIGN, 'expecting assign')
        self.expr()

        
    
    def call_expr(self):
        
        """ ID LPAREN ( <expr> ( COMMA <expr> )∗ | ϵ ) RPAREN"""
        """ID already read when called"""
        self.eat(TokenType.LPAREN, 'expecting LPAREN') 
        while not self.match(TokenType.RPAREN):
            self.expr()
            if not self.match(TokenType.RPAREN):
                self.eat(TokenType.COMMA, 'expecting comma')
                if(self.match(TokenType.RPAREN)):
                    self.error('extra comma')
        
        self.eat(TokenType.RPAREN, 'expecting rparen')


    def expr(self):
       
        """( <rvalue> | NOT <expr> | LPAREN <expr> RPAREN ) ( <bin_op> <expr> | ϵ )"""
        if self.match(TokenType.NOT):
            self.advance()
            self.expr()
        elif self.match(TokenType.LPAREN):
            self.advance()
            self.expr()
            self.eat(TokenType.RPAREN, 'expected RPAREN')
        else:
            self.rvalue()
        if(self.is_bin_op()):
            self.advance()
            self.expr()

        
    
    def rvalue(self):
        
       
        """<base_rvalue> | NULL_VAL | <new_rvalue> | <var_rvalue> | <call_expr>"""
       
        if(self.match(TokenType.NULL_VAL)):
            self.advance()
        elif(self.match(TokenType.NEW)):
            self.new_rvalue()
        elif(self.match(TokenType.ID)):
            self.advance()
            if(self.match(TokenType.LPAREN)):
                self.call_expr()
            else:
                self.var_rvalue()
        else:
            self.base_rvalue()
    
    def base_rvalue(self):
         
         """ INT_VAL | DOUBLE_VAL | BOOL_VAL | STRING_VAL"""
         types = [TokenType.INT_VAL, TokenType.DOUBLE_VAL, TokenType.BOOL_VAL, TokenType.STRING_VAL]
   
         if self.match_any(types):
            
            self.advance()
         else:
            self.error('expecting base type value')

    
    def new_rvalue(self):
       
       """ NEW ID LPAREN ( <expr> ( COMMA <expr> )∗| ϵ ) RPAREN |
       NEW ( ID | <base_type> ) LBRACKET <expr> RBRACKET"""
       self.eat(TokenType.NEW, 'expecting new') # eats new
      
       if(self.match(TokenType.ID)):
            self.advance() # eats ID
            if(self.match(TokenType.LPAREN)):
                self.advance() # eat lparen
                while not self.match(TokenType.RPAREN):
                    self.expr()
                    if not self.match(TokenType.RPAREN):
                        self.eat(TokenType.COMMA, "expecting COMMA")
                        if(self.match(TokenType.RPAREN)):
                            self.error('extra comma')
                self.eat(TokenType.RPAREN, 'expecting RPAREN')
            else:
                self.eat(TokenType.LBRACKET, 'expecting LBRACKET')
                self.expr()
                self.eat(TokenType.RBRACKET, 'expecting RBRACKET')
       else:
           self.base_type()
           self.eat(TokenType.LBRACKET, 'expecting LBRACKET')
           self.expr()
           self.eat(TokenType.RBRACKET, 'expecting RBRACKET')

           

       


    def var_rvalue(self):
        
        """ID ( LBRACKET <expr> RBRACKET | ϵ ) ( DOT ID ( LBRACKET <expr> RBRACKET | ϵ ) )*"""
        """ID is eaten when called"""
        if(self.match(TokenType.LBRACKET)):
            self.advance()
            self.expr()
            self.eat(TokenType.RBRACKET, 'expecting RBRACKET')
        while self.match(TokenType.DOT):
            self.advance() # eat dot
            self.eat(TokenType.ID, 'expexting ID after dot')
            if(self.match(TokenType.LBRACKET)):
                self.advance()
                self.expr()
                self.eat(TokenType.RBRACKET, 'expecting RBRACKED')
            

    def bin_op(self):
        
        if(self.is_bin_op):
            self.advance()
        else:
            self.error("expected binary operator")
    

    # TODO: Define the rest of the needed recursive descent functions
