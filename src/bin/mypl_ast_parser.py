"""MyPL AST parser implementation.

NAME: <your-name-here>
DATE: Spring 2024
CLASS: CPSC 326
"""

from mypl_error import *
from mypl_token import *
from mypl_lexer import *
from mypl_ast import *


class ASTParser:

    def __init__(self, lexer):
        """Create a MyPL syntax checker (parser). 
        
        Args:
            lexer -- The lexer to use in the parser.

        """
        self.lexer = lexer
        self.curr_token = None

        
    def parse(self):
        """Start the parser, returning a Program AST node."""
        program_node = Program([], [])
        self.advance()
        while not self.match(TokenType.EOS):
            if self.match(TokenType.STRUCT):
                self.struct_def(program_node)
            else:
                self.fun_def(program_node)
        self.eat(TokenType.EOS, 'expecting EOF')
        return program_node

        
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
        """Returns true if the current token is a binary operator."""
        ts = [TokenType.PLUS, TokenType.MINUS, TokenType.TIMES, TokenType.DIVIDE,
              TokenType.AND, TokenType.OR, TokenType.EQUAL, TokenType.LESS,
              TokenType.GREATER, TokenType.LESS_EQ, TokenType.GREATER_EQ,
              TokenType.NOT_EQUAL]
        return self.match_any(ts)


    #----------------------------------------------------------------------
    # Recursive descent functions
    #----------------------------------------------------------------------


    # TODO: Finish the recursive descent functions below. Note that
    # you should copy in your functions from HW-2 and then instrument
    # them to build the corresponding AST objects.

    def struct_def(self, program_node):
        """Check for well-formed struct definition."""
        
        struct_def_node = StructDef(None, []) 
        
        self.eat(TokenType.STRUCT, 'expecting struct')

        struct_def_node.struct_name = self.curr_token

        self.eat(TokenType.ID, 'expecting ID')
        self.eat(TokenType.LBRACE, 'expecting left brace')
        self.fields(struct_def_node)
        self.eat(TokenType.RBRACE, 'expecting right brace')

        program_node.struct_defs.append(struct_def_node)
        
       
        # TODO
        
    def fields(self, struct_def_node):
        
        """Check for well-formed struct fields."""
        """ <data_type> ID ( SEMICOLON <data_type> ID )* | ϵ
"""
        types = [TokenType.INT_TYPE, TokenType.BOOL_TYPE, TokenType.VOID_TYPE, 
                 TokenType.DOUBLE_TYPE, TokenType.STRING_TYPE]
        
        while not self.match(TokenType.RBRACE):
            data_type_node = DataType(None, None)
            var_def_node = VarDef(data_type_node, None)
            self.data_type(data_type_node)
            var_def_node.var_name = self.curr_token
            self.eat(TokenType.ID, 'expecting ID')
            self.eat(TokenType.SEMICOLON, 'expecting semicolon')
            struct_def_node.fields.append(var_def_node)
       
        # TODO
            
    def fun_def(self, program_node):
        
        """Check for well-formed function definition."""
        """<fun_def> ::= ( <data_type> | VOID_TYPE ) ID LPAREN <params> RPAREN LBRACE ( <stmt> )∗ RBRACE"""
        data_type_node = DataType(None, None)
        fun_def_node = FunDef(data_type_node, None, [], [])
        program_node.fun_defs.append(fun_def_node)
        if(self.match(TokenType.VOID_TYPE)):
            data_type_node.is_array = False
            data_type_node.type_name = self.curr_token
            self.advance()
        else:
            self.data_type(data_type_node)
        fun_def_node.fun_name = self.curr_token
        self.eat(TokenType.ID, 'expecting functon name of ID type')
        self.eat(TokenType.LPAREN, 'expecting left paren')
        self.params(fun_def_node)
        self.eat(TokenType.RPAREN, 'expected right paren')
        self.eat(TokenType.LBRACE, 'expected left brace')

       
       
        while not self.match(TokenType.RBRACE):
            self.stmt(fun_def_node.stmts)
           
           
        self.eat(TokenType.RBRACE, 'expected right brace')
        
        # TODO

    def params(self, fun_def_node):
        """Check for well-formed function formal parameters."""
        
        while not self.match(TokenType.RPAREN):
            data_type = DataType(None, None)
            param_node = VarDef(data_type, None)
            self.data_type(data_type)
            param_node.var_name = self.curr_token
            self.eat(TokenType.ID, 'expecting paramater name of type ID ')
            if not self.match(TokenType.RPAREN):
                self.eat(TokenType.COMMA, 'expecting comma')
                if(self.match(TokenType.RPAREN)):
                    self.error('extra comma')
            fun_def_node.params.append(param_node)
        # TODO
    def data_type(self, data_type_node):
        
        """ # <data_type> ::= <base_type> | ID | ARRAY ( <base_type> | ID )"""
        #data_type_node = DataType(None, None)
        data_type_node.is_array = False
        if(self.match(TokenType.ID)):
            data_type_node.type_name = self.curr_token
            self.advance()
        elif (self.match(TokenType.ARRAY)):
            data_type_node.is_array = True
            self.advance()
            data_type_node.type_name = self.curr_token
            if(self.match(TokenType.ID)):
                self.advance()
            else:
                self.base_type()
        else:
            data_type_node.type_name = self.curr_token
            self.base_type()
   
    def base_type(self):
        
        """ # <base_type> ::= INT_TYPE | DOUBLE_TYPE | BOOL_TYPE | STRING_TYPE"""
        types = [TokenType.INT_TYPE, TokenType.BOOL_TYPE, 
                 TokenType.DOUBLE_TYPE, TokenType.STRING_TYPE]
        if(self.match_any(types)):
            self.advance()
        else:
            self.error('expected base type')
        
    def stmt(self, stmt_list_node):
        
        """<while_stmt> | <if_stmt> | <for_stmt> | <return_stmt> SEMICOLON |
        <vdecl_stmt> SEMICOLON | <assign_stmt> SEMICOLON | <call_expr> SEMICOLON"""
        stmt_node = None
        if(self.match(TokenType.WHILE)):
            stmt_node = WhileStmt(None, [])
            self.while_stmt(stmt_node)
            
        elif(self.match(TokenType.IF)):
            stmt_node = IfStmt(None, [], [])
            self.if_stmt(stmt_node)
        elif(self.match(TokenType.FOR)):
            stmt_node = ForStmt(None, None, None, [])
            self.for_stmt(stmt_node)
        elif(self.match(TokenType.RETURN)):
            stmt_node = ReturnStmt(None)
            self.return_stmt(stmt_node)
            self.eat(TokenType.SEMICOLON, 'expecting semicolon')
        elif(self.match(TokenType.ID)):
            token_save = self.curr_token
            self.advance()
            if(self.match(TokenType.LPAREN)):
                stmt_node = CallExpr(token_save, [])
                self.call_expr(stmt_node)
                self.eat(TokenType.SEMICOLON, 'expected semicolon')
            elif(self.match(TokenType.LBRACKET) or self.match(TokenType.DOT) or self.match(TokenType.ASSIGN)):
                stmt_node = AssignStmt([], None)
                self.assign_stmt(stmt_node)
                stmt_node.lvalue[0].var_name = token_save
                self.eat(TokenType.SEMICOLON, 'expected semicolon')
            else:
                stmt_node = VarDecl(None, None)
               
                self.vdecl_stmt(True, stmt_node)
                stmt_node.var_def.data_type.type_name = token_save
                self.eat(TokenType.SEMICOLON, 'expected semicolon')
        else:
            stmt_node = VarDecl(None, None)
        
            self.vdecl_stmt(False, stmt_node)
            self.eat(TokenType.SEMICOLON, 'expected semicolon')
        
        stmt_list_node.append(stmt_node)
            


    
    def while_stmt(self, while_stmt_node):
        
        """ WHILE LPAREN <expr> RPAREN LBRACE ( <stmt> )∗ RBRACE"""
        
        expr_node = Expr(None, None, None, None)
        while_stmt_node.condition = expr_node
    
        self.eat(TokenType.WHILE, "expected while")
        self.eat(TokenType.LPAREN, 'expected l paren')
        self.expr(while_stmt_node.condition)
        self.eat(TokenType.RPAREN, 'expected r paren')
        self.eat(TokenType.LBRACE, 'expected l brace')
        while(not self.match(TokenType.RBRACE)):
            
            self.stmt(while_stmt_node.stmts)
            #while_stmt_node.stmts.append(stmt_node)
        self.eat(TokenType.RBRACE, 'expecting RBRACE')
        


    def if_stmt(self, if_stmt_node):
        
        """IF LPAREN <expr> RPAREN LBRACE ( <stmt> )∗ RBRACE <if_stmt_t>"""
        if_stmt_node.if_part = BasicIf(None, [])
        self.eat(TokenType.IF, 'expecting IF')# eats if
        self.eat(TokenType.LPAREN, 'expecting LPAREN')
        if_stmt_node.if_part.condition = Expr(None, None, None, None)
        self.expr(if_stmt_node.if_part.condition)
        self.eat(TokenType.RPAREN, 'expecting RPAREN')
        self.eat(TokenType.LBRACE, 'expecting LBRACE')
        while not self.match(TokenType.RBRACE):
            self.stmt(if_stmt_node.if_part.stmts)
        self.eat(TokenType.RBRACE, 'expecting RBRACE')
        self.if_stmt_t(if_stmt_node)


    def if_stmt_t(self, if_stmt_node):
        
        """ELSEIF LPAREN <expr> RPAREN LBRACE ( <stmt> )∗ RBRACE <if_stmt_t> | ELSE LBRACE ( <stmt> )∗ RBRACE | ϵ"""
        if self.match(TokenType.ELSEIF):
            else_if_node = BasicIf(Expr(None, None, None, None), [])
            self.advance()
            self.eat(TokenType.LPAREN, 'expecting LPAREN')
            self.expr(else_if_node.condition)
            self.eat(TokenType.RPAREN, 'expecting RPAREN')
            self.eat(TokenType.LBRACE, 'expecting LBRACE')
            while not self.match(TokenType.RBRACE):
                self.stmt(else_if_node.stmts)
            self.eat(TokenType.RBRACE, 'expecting RBRACE')
            if_stmt_node.else_ifs.append(else_if_node)
            self.if_stmt_t(if_stmt_node)
        elif self.match(TokenType.ELSE):
            self.advance()
            self.eat(TokenType.LBRACE, 'expecting LBRACE')
            while not self.match(TokenType.RBRACE):
                self.stmt(if_stmt_node.else_stmts)
            self.eat(TokenType.RBRACE, 'expecting RBRACE')
        

    def for_stmt(self, for_stmt_node):
       
        """FOR LPAREN <vdecl_stmt> SEMICOLON <expr> SEMICOLON <assign_stmt> <RPAREN> LBRACE ( <stmt> )∗ RBRACE"""
        self.eat(TokenType.FOR, 'expecting for') # eats for
        self.eat(TokenType.LPAREN, 'expected LPAREN')
        for_stmt_node.var_decl = VarDecl(None, None)
        self.vdecl_stmt(False, for_stmt_node.var_decl)
        self.eat(TokenType.SEMICOLON, 'expected SEMICOLON')
        for_stmt_node.condition = Expr(None, None, None, None)
        self.expr(for_stmt_node.condition)
        self.eat(TokenType.SEMICOLON, 'expected SEMICOLON')
        
        token_save = self.curr_token
        self.eat(TokenType.ID, 'expecting ID') # as a part of the assign_stmt grammar
        for_stmt_node.assign_stmt = AssignStmt([], None)
        self.assign_stmt(for_stmt_node.assign_stmt)
        for_stmt_node.assign_stmt.lvalue[0].var_name = token_save
        self.eat(TokenType.RPAREN, 'expected RPAREN')
        self.eat(TokenType.LBRACE, 'expected LBRACE')
        while not self.match(TokenType.RBRACE):
                self.stmt(for_stmt_node.stmts)
        self.eat(TokenType.RBRACE, 'expected RBRACE')

    
    def return_stmt(self, return_stmt_node):
       
        """RETURN <expr> SEMICOLON"""
        self.eat(TokenType.RETURN, 'expecting return')
        return_stmt_node.expr = Expr(None, None, None, None)
        self.expr(return_stmt_node.expr)
        # self.eat(TokenType.SEMICOLON, 'expecting semicolon')

    def lvalue(self, l_val_list):
        
        """ ID ( LBRACKET <expr> RBRACKET | ϵ ) ( DOT ID ( LBRACKET <expr> RBRACKET | ϵ ) )∗"""
        """ID already eaten"""
        var_ref_node = VarRef(None, None)
        var_ref_node.var_name = self.curr_token
        l_val_list.append(var_ref_node)
        
        if(self.match(TokenType.LBRACKET)):
            self.advance()
            var_ref_node.array_expr = Expr(None, None, None, None)
            self.expr(var_ref_node.array_expr)
            self.eat(TokenType.RBRACKET, 'expecting RBRACKET')

        while(self.match(TokenType.DOT)):
            self.advance()
            var_ref_node = VarRef(self.curr_token, None)
            self.eat(TokenType.ID, 'expecting ID')
            if(self.match(TokenType.LBRACKET)):
                self.advance()
                var_ref_node.array_expr = Expr(None, None, None, None)
                self.expr(var_ref_node.array_expr)
                self.eat(TokenType.RBRACKET, 'expecting RBRACKET')
            l_val_list.append(var_ref_node)
               
    def vdecl_stmt(self, ifIdRead, var_decl_node):
        
        """<data_type> ID ( ASSIGN <expr> | ϵ )"""
        """ID already read when called"""
        var_decl_node.var_def = VarDef(None, None)

        if not ifIdRead:
            var_decl_node.var_def.data_type = DataType(None, None)
            self.data_type(var_decl_node.var_def.data_type)
        else:
            var_decl_node.var_def.data_type = DataType(False, None)
        var_decl_node.var_def.var_name = self.curr_token
        self.eat(TokenType.ID, 'expected ID')
        if not self.match(TokenType.SEMICOLON):
            var_decl_node.expr = Expr(None, None, None, None)
            self.eat(TokenType.ASSIGN, 'expected =')
            self.expr(var_decl_node.expr)
        
    
    def assign_stmt (self, assign_stmt_node):
       
        """<lvalue> ASSIGN <expr>"""
        """ID already read when called"""
        
        self.lvalue(assign_stmt_node.lvalue)
        self.eat(TokenType.ASSIGN, 'expecting assign')
        assign_stmt_node.expr = Expr(None, None, None, None)
        self.expr(assign_stmt_node.expr)

        
    
    def call_expr(self, call_expr_node):
        
        """ ID LPAREN ( <expr> ( COMMA <expr> )∗ | ϵ ) RPAREN"""
        """ID already read when called"""
        self.eat(TokenType.LPAREN, 'expecting LPAREN') 
        while not self.match(TokenType.RPAREN):
            expr_node = Expr(None, None, None, None)
            self.expr(expr_node)
            call_expr_node.args.append(expr_node)
            if not self.match(TokenType.RPAREN):
                self.eat(TokenType.COMMA, 'expecting comma')
                if(self.match(TokenType.RPAREN)):
                    self.error('extra comma')
        
        self.eat(TokenType.RPAREN, 'expecting rparen')


    def expr(self, expr_node):
       
        """( <rvalue> | NOT <expr> | LPAREN <expr> RPAREN ) ( <bin_op> <expr> | ϵ )"""
        expr_node.not_op = False
        if self.match(TokenType.NOT):
            
            self.advance()
            self.expr(expr_node)
            expr_node.not_op = True

        elif self.match(TokenType.LPAREN):
            first_node = ComplexTerm(Expr(None, None, None, None))
            self.advance()
            self.expr(first_node.expr)
            self.eat(TokenType.RPAREN, 'expected RPAREN')
            expr_node.first = first_node
        else:
            first_node = SimpleTerm(None)
            self.rvalue(first_node)
            expr_node.first = first_node
       
        if(self.is_bin_op()):
            expr_node.op = self.curr_token
            self.advance()
            expr_node.rest = Expr(None, None, None, None)
            self.expr(expr_node.rest)

        
    
    #r val is term
    def rvalue(self, term_node):

        """<base_rvalue> | NULL_VAL | <new_rvalue> | <var_rvalue> | <call_expr>"""
       
        if(self.match(TokenType.NULL_VAL)):
            term_node.rvalue = SimpleRValue(None)
            term_node.rvalue.value = self.curr_token
            self.advance()
        elif(self.match(TokenType.NEW)):
            term_node.rvalue = NewRValue(None, None, None)
            self.new_rvalue(term_node.rvalue)
        elif(self.match(TokenType.ID)):
            token_save = self.curr_token
            self.advance()
            if(self.match(TokenType.LPAREN)):
                term_node.rvalue = CallExpr(token_save, [])
                self.call_expr(term_node.rvalue)
            else:
                term_node.rvalue = VarRValue([])
                self.var_rvalue(term_node.rvalue)
                term_node.rvalue.path[0].var_name = token_save
        else:
            term_node.rvalue = SimpleRValue(None)
            self.base_rvalue(term_node.rvalue)
           
    
    def base_rvalue(self, r_val_node):
         
         """ INT_VAL | DOUBLE_VAL | BOOL_VAL | STRING_VAL"""
         types = [TokenType.INT_VAL, TokenType.DOUBLE_VAL, TokenType.BOOL_VAL, TokenType.STRING_VAL]

         r_val_node.value = self.curr_token
         if self.match_any(types):
            self.advance()
         else:
            self.error('expecting base type value')

    """
    r_val_node is type NewRVal
    type_name: Token
    array_expr : Expr
    struct_params: [Expr]

    """
    def new_rvalue(self, r_val_node):
       
       """ NEW ID LPAREN ( <expr> ( COMMA <expr> )∗| ϵ ) RPAREN |
       NEW ( ID | <base_type> ) LBRACKET <expr> RBRACKET"""
       self.eat(TokenType.NEW, 'expecting new') # eats new
       
       r_val_node.type_name = self.curr_token
       if(self.match(TokenType.ID)):
            
            self.advance() # eats ID
            if(self.match(TokenType.LPAREN)):
                r_val_node.struct_params = []
                self.advance() # eat lparen
                while not self.match(TokenType.RPAREN):
                    # r_val_node.struct_params = []
                    expr_node = Expr(None, None, None, None)
                    self.expr(expr_node)
                    r_val_node.struct_params.append(expr_node)
                    if not self.match(TokenType.RPAREN):
                        self.eat(TokenType.COMMA, "expecting COMMA")
                        if(self.match(TokenType.RPAREN)):
                            self.error('extra comma')
                self.eat(TokenType.RPAREN, 'expecting RPAREN')
            else:
                self.eat(TokenType.LBRACKET, 'expecting LBRACKET')
                r_val_node.array_expr = Expr(None, None, None, None)
                self.expr(r_val_node.array_expr)
                self.eat(TokenType.RBRACKET, 'expecting RBRACKET')
       else:
           self.base_type()
           self.eat(TokenType.LBRACKET, 'expecting LBRACKET')
           r_val_node.array_expr = Expr(None, None, None, None)
           self.expr(r_val_node.array_expr)
           self.eat(TokenType.RBRACKET, 'expecting RBRACKET')

           

       
    """
    var_rval_node is type VarRVal
    path : [VarRef]

    VarRef:
    var_name : Token
    array_expr : Expr
    """
    def var_rvalue(self, var_rval_node):
        
        """ID ( LBRACKET <expr> RBRACKET | ϵ ) ( DOT ID ( LBRACKET <expr> RBRACKET | ϵ ) )*"""
        """ID is eaten when called"""
        var_rval_node.path.append(VarRef(None, None))
        
        if(self.match(TokenType.LBRACKET)):
            self.advance()
            var_rval_node.path[0].array_expr = Expr(None, None, None, None)
            self.expr(var_rval_node.path[0].array_expr)
            self.eat(TokenType.RBRACKET, 'expecting RBRACKET')
        while self.match(TokenType.DOT):
            self.advance() # eat dot
            var_ref_node = VarRef(self.curr_token, None)
            self.eat(TokenType.ID, 'expecting ID after dot')
            if(self.match(TokenType.LBRACKET)):
                var_ref_node.array_expr = Expr(None, None, None, None)
                self.advance()
                self.expr(var_ref_node.array_expr)
                self.eat(TokenType.RBRACKET, 'expecting RBRACKET')
            var_rval_node.path.append(var_ref_node)
            

    def bin_op(self):
        
        if(self.is_bin_op):
            self.advance()
        else:
            self.error("expected binary operator")
    
