"""Semantic Checker Visitor for semantically analyzing a MyPL program.

NAME: <Ryan St. Mary>
DATE: Spring 2024
CLASS: CPSC 326

"""
import pdb
from dataclasses import dataclass
from mypl_error import *
from mypl_token import Token, TokenType
from mypl_ast import *
from mypl_symbol_table import SymbolTable


BASE_TYPES = ['int', 'double', 'bool', 'string']
BUILT_INS = ['print', 'input', 'itos', 'itod', 'dtos', 'dtoi', 'stoi', 'stod',
             'length', 'get']

class SemanticChecker(Visitor):
    """Visitor implementation to semantically check MyPL programs."""

    def __init__(self):
        self.structs = {}
        self.functions = {}
        self.symbol_table = SymbolTable()
        self.curr_type = None


    # Helper Functions

    def error(self, msg, token):
        """Create and raise a Static Error."""
        if token is None:
            raise StaticError(msg)
        else:
            m = f'{msg} near line {token.line}, column {token.column}'
            raise StaticError(m)


    def get_field_type(self, struct_def, field_name):
        """Returns the DataType for the given field name of the struct
        definition.

        Args:
            struct_def: The StructDef object 
            field_name: The name of the field

        Returns: The corresponding DataType or None if the field name
        is not in the struct_def.

        """
        for var_def in struct_def.fields:
            if var_def.var_name.lexeme == field_name:
                return var_def.data_type
        return None

        
    # Visitor Functions
    
    def visit_program(self, program):
        # check and record struct defs
        for struct in program.struct_defs:
            struct_name = struct.struct_name.lexeme
            if struct_name in self.structs:
                self.error(f'duplicate {struct_name} definition', struct.struct_name)
            self.structs[struct_name] = struct
        # check and record function defs
        for fun in program.fun_defs:
            fun_name = fun.fun_name.lexeme
            if fun_name in self.functions:
                self.error(f'duplicate {fun_name} definition', fun.fun_name)
            if fun_name in BUILT_INS:
                self.error(f'redefining built-in function', fun.fun_name)
            if fun_name == 'main' and fun.return_type.type_name.lexeme != 'void':
                self.error('main without void type', fun.return_type.type_name)
            if fun_name == 'main' and fun.params: 
                self.error('main function with parameters', fun.fun_name)
            self.functions[fun_name] = fun
        # check main function
        if 'main' not in self.functions:
            self.error('missing main function', None)
        # check each struct
        for struct in self.structs.values():
            struct.accept(self)
        # check each function
        for fun in self.functions.values():
            fun.accept(self)
        
        
    def visit_struct_def(self, struct_def):
        self.symbol_table.push_environment()
        for field in struct_def.fields:
            field.accept(self)
        self.symbol_table.pop_environment()
        

    def visit_fun_def(self, fun_def):
        self.symbol_table.push_environment()
        if fun_def.return_type.type_name.lexeme not in (BASE_TYPES+['void']) and fun_def.return_type.type_name.lexeme not in self.structs:
            # print(self.structs)
            self.error('invalid return type', fun_def.return_type.type_name) 
        self.symbol_table.add('return', fun_def.return_type)
        for param in fun_def.params:
            param.accept(self)
            
        for stmt in fun_def.stmts:
            stmt.accept(self)
        self.symbol_table.pop_environment()
        
        
    def visit_return_stmt(self, return_stmt):
        # TODO
        return_stmt.expr.accept(self)
        if self.curr_type.type_name.lexeme not in [ self.symbol_table.get('return').type_name.lexeme, 'void']:
            self.error('invalid return type', None)
        
        
            
    def visit_var_decl(self, var_decl):
        var_decl.var_def.accept(self)
        lval_type = self.curr_type
        if var_decl.expr != None:
            var_decl.expr.accept(self)
        
       
        
        if (lval_type.type_name.lexeme != self.curr_type.type_name.lexeme
           or lval_type.is_array != self.curr_type.is_array) and self.curr_type.type_name.lexeme != 'void':
            self.error('mismatched type in variable declaration', var_decl.var_def.var_name)
        
        
            
        
    def visit_assign_stmt(self, assign_stmt):
        ltype = DataType(None, None)

        if not self.symbol_table.exists(assign_stmt.lvalue[0].var_name.lexeme):
            self.error(assign_stmt.lvalue[0].var_name.lexeme + 'doesnt exist', assign_stmt.lvalue[0].var_name)
        first_type = self.symbol_table.get(assign_stmt.lvalue[0].var_name.lexeme)
        ltype.is_array = first_type.is_array
        ltype.type_name = first_type.type_name

        if ltype.is_array and assign_stmt.lvalue[0].array_expr != None:
            ltype.is_array = False


        f_type = None
        i = 1
        l_len = len(assign_stmt.lvalue)
        if first_type.type_name.lexeme not in BASE_TYPES:
            struct = self.structs[first_type.type_name.lexeme]
        while i < l_len:
            
            f_type = self.get_field_type(struct, assign_stmt.lvalue[i].var_name.lexeme)
            if f_type == None:
                self.error('bad type name', assign_stmt.lvalue[i].var_name)
            first_type = DataType(f_type.is_array, f_type.type_name)
            # 
            # if is array and no array expr and not last item in list
            if f_type.is_array and assign_stmt.lvalue[i].array_expr == None and i < l_len-1:
                self.error('array type not indexed in middle of path', assign_stmt.lvalue[i].var_name)
            # if array expr but not isarray
            if not f_type.is_array and assign_stmt.lvalue[i].array_expr != None:
                self.error('trying to index non-array type', assign_stmt.lvalue[i].var_name)
            # if array expr but not isarray
            
            if f_type.is_array and assign_stmt.lvalue[i].array_expr != None:
                first_type.is_array = False
            
            i = i+1
            if i < len(assign_stmt.lvalue):
                struct = self.structs[first_type.type_name.lexeme]

        if l_len > 1:
            ltype = first_type
       
        # curr type = expr  type
        assign_stmt.expr.accept(self)
        
        
        # pdb.set_trace()

        if ([self.curr_type.type_name.lexeme, self.curr_type.is_array] != 
            [ltype.type_name.lexeme, ltype.is_array] and self.curr_type.type_name.lexeme != 'void'):
            self.error('mismatched types in assignment statement', assign_stmt.lvalue[0].var_name)



        
            
    def visit_while_stmt(self, while_stmt):
        # TODO
        self.symbol_table.push_environment()
        while_stmt.condition.accept(self)
        
      

        if self.curr_type.type_name.lexeme != 'bool' or self.curr_type.is_array:
            self.error('non boolean while condition', self.curr_type.type_name)
        
        for stmt in while_stmt.stmts:
            stmt.accept(self)
        self.symbol_table.pop_environment()
        
    def visit_for_stmt(self, for_stmt):
        # TODO
        self.symbol_table.push_environment()
        for_stmt.var_decl.accept(self)
        for_stmt.condition.accept(self)
        if self.curr_type.type_name.lexeme != 'bool' or self.curr_type.is_array:
            self.error('non boolean for condition', None)
        for_stmt.assign_stmt.accept(self)

        for stmt in for_stmt.stmts:
            stmt.accept(self)
        self.symbol_table.pop_environment()
        
    def visit_if_stmt(self, if_stmt):
        # TODO
        self.symbol_table.push_environment()
        if_stmt.if_part.condition.accept(self)
        if self.curr_type.type_name.lexeme != 'bool'or self.curr_type.is_array:
            self.error('non-bool type in if condition', None)
        for stmt in if_stmt.if_part.stmts:
            stmt.accept(self)
        self.symbol_table.pop_environment()

        
        for else_if in if_stmt.else_ifs:
            self.symbol_table.push_environment()
            else_if.condition.accept(self)
            if self.curr_type.type_name.lexeme != 'bool' or self.curr_type.is_array:
                self.error('non-bool type in if condition', None)
            for stmt in else_if.stmts:
                stmt.accept(self)
            self.symbol_table.pop_environment()
        
        self.symbol_table.push_environment()
        for stmt in if_stmt.else_stmts:  
            stmt.accept(self)
        self.symbol_table.pop_environment()      

        
        
    def visit_call_expr(self, call_expr):
        # TODO
        # ['print', 'input', 'itos', 'itod', 'dtos', 'dtoi', 'stoi', 'stod',
         #    'length', 'get']
        f_name = call_expr.fun_name.lexeme

        if f_name == 'print':
            if len(call_expr.args) != 1:
                self.error('wrong number of arguments in print', call_expr.fun_name)
            call_expr.args[0].accept(self)
            if self.curr_type.type_name.lexeme not in ['string', 'double', 'int', 'bool'] or self.curr_type.is_array:
                self.error('non string arg in print', call_expr.fun_name)
            self.curr_type = DataType(False, Token(TokenType.VOID_TYPE, 'void', None, None))
            return

        if f_name == 'input':
            if len(call_expr.args) != 0:
                self.error('wrong number of arguments in input', call_expr.fun_name)
            self.curr_type = DataType(False, Token(TokenType.STRING_TYPE, 'string', None, None))
            return
        
        if f_name == 'itos':
            if len(call_expr.args) != 1:
                self.error('wrong number of arguments in itos', call_expr.fun_name)
            call_expr.args[0].accept(self)
            if self.curr_type.type_name.lexeme != 'int' or self.curr_type.is_array:
                self.error('non int arg in itos', call_expr.fun_name)
            self.curr_type = DataType(False, Token(TokenType.STRING_TYPE, 'string', None, None))
            return
        
        if f_name == 'itod':
            if len(call_expr.args) != 1:
                self.error('wrong number of arguments in itos', call_expr.fun_name)
            call_expr.args[0].accept(self)
            if self.curr_type.type_name.lexeme != 'int' or self.curr_type.is_array:
                self.error('non int arg in itod', call_expr.fun_name)
            self.curr_type = DataType(False, Token(TokenType.DOUBLE_TYPE, 'double', None, None))
            return
        
        if f_name == 'dtos':
            if len(call_expr.args) != 1:
                self.error('wrong number of arguments in dtos', call_expr.fun_name)
            call_expr.args[0].accept(self)
            if self.curr_type.type_name.lexeme != 'double' or self.curr_type.is_array:
                self.error('non double arg in dtos', call_expr.fun_name)
            self.curr_type = DataType(False, Token(TokenType.STRING_TYPE, 'string', None, None))
            return

        if f_name == 'dtoi':
            if len(call_expr.args) != 1:
                self.error('wrong number of arguments in dtoi', call_expr.fun_name)
            call_expr.args[0].accept(self)
            if self.curr_type.type_name.lexeme != 'double' or self.curr_type.is_array:
                self.error('non double arg in dtoi', call_expr.fun_name)
            self.curr_type = DataType(False, Token(TokenType.INT_TYPE, 'int', None, None))
            return
        
        if f_name == 'stoi':
            if len(call_expr.args) != 1:
                self.error('wrong number of arguments in stoi', call_expr.fun_name)
            call_expr.args[0].accept(self)
            if self.curr_type.type_name.lexeme != 'string' or self.curr_type.is_array:
                self.error('non string arg in stoi', call_expr.fun_name)
            self.curr_type = DataType(False, Token(TokenType.INT_TYPE, 'int', None, None))
            return
        
        if f_name == "stod":
            if len(call_expr.args) != 1:
                self.error('wrong number of arguments in stod', call_expr.fun_name)
            call_expr.args[0].accept(self)
            if self.curr_type.type_name.lexeme != 'string' or self.curr_type.is_array:
                self.error('non string arg in stod', call_expr.fun_name)
            self.curr_type = DataType(False, Token(TokenType.DOUBLE_TYPE, 'double', None, None))
            return
        
        if f_name == 'length':
            if len(call_expr.args) != 1:
                self.error('wrong number of arguments in length', call_expr.fun_name)
            call_expr.args[0].accept(self)
            if self.curr_type.type_name.lexeme != 'string' and not self.curr_type.is_array:
                self.error('invalid arg in length', call_expr.fun_name)
            self.curr_type = DataType(False, Token(TokenType.INT_TYPE, 'int', None, None))
            return
        
        if f_name == 'get':
            if len(call_expr.args) != 2:
                self.error('wrong number of arguments in length', call_expr.fun_name)
            call_expr.args[0].accept(self)
            if self.curr_type.type_name.lexeme != 'int':
                self.error('invalid arg in length', call_expr.fun_name)
            call_expr.args[1].accept(self)
            if self.curr_type.type_name.lexeme != 'string' or self.curr_type.is_array:
                self.error('invalid arg in length', call_expr.fun_name)
            self.curr_type = DataType(False, Token(TokenType.STRING_TYPE, 'string', None, None))
            return
        

        if f_name not in self.functions:
            self.error('function doesnt exist', call_expr.fun_name)
        fun_def = self.functions[call_expr.fun_name.lexeme]

        if(len(call_expr.args) != len(fun_def.params)):
            self.error('wrong amount of params', call_expr.fun_name)
        i = 0
        for arg in call_expr.args:
            arg.accept(self)
            if self.curr_type.type_name.lexeme not in [fun_def.params[i].data_type.type_name.lexeme, 'void']:
                self.error('invalid parameter type', arg.first.rvalue.value)  
            i = i+1
        self.curr_type = fun_def.return_type
        
        

    def visit_expr(self, expr):
        expr.first.accept(self)
        first_type = self.curr_type
        
        if expr.op != None:
            expr.rest.accept(self)
            rest_type = self.curr_type
            
        is_arr = False
        if expr.op != None:
            f_type_name = first_type.type_name.lexeme
            r_type_name = rest_type.type_name.lexeme

            
        
            
            type_token = Token(None, None, None, None)
            
            if f_type_name != r_type_name and (r_type_name != 'void' and f_type_name != 'void'):
                self.error('type error', expr.op)
            elif expr.op.lexeme in ['<', '<=', '>', '>=']:
                if r_type_name == 'bool':
                    self.error('bool in relational comparision', expr.op)
                type_token.token_type = TokenType.BOOL_TYPE
                type_token.lexeme = 'bool'
            elif expr.op.lexeme in ['and', 'or']:
                if f_type_name != 'bool' or r_type_name != 'bool':
                    self.error('non bool with and/or', expr.op)
                type_token.token_type = TokenType.BOOL_TYPE
                type_token.lexeme = 'bool'
            elif expr.op.lexeme in ['==', '!=']:
                type_token.token_type = TokenType.BOOL_TYPE
                type_token.lexeme = 'bool'
            elif expr.op.lexeme in ['+', '-', '*', '/']:
                if f_type_name != r_type_name:
                    self.error('mismatched types in operation', expr.op)
                type_token.token_type = first_type.type_name.token_type
                type_token.lexeme = f_type_name
            elif f_type_name == 'string' and r_type_name == 'string':
                if expr.op.lexeme not in ['+', '==', '!=']:
                    self.error('invalid operator on a string', expr.op)
                elif expr.op.lexeme == '+':
                    type_token.token_type = TokenType.STRING_TYPE
                    type_token.lexeme = 'string'
                elif expr.op.lexeme in ['==', '!=']:
                    type_token.token_type == TokenType.BOOL_TYPE
                    type_token.lexeme = 'bool'
            self.curr_type = DataType(is_arr, type_token)

            
        

     
        if expr.not_op and self.curr_type.type_name.lexeme != 'bool':
            self.error('not on invalid type', expr.op)        
       
        

    def visit_data_type(self, data_type):
        # note: allowing void (bad cases of void caught by parser)
        name = data_type.type_name.lexeme
        if name == 'void' or name in BASE_TYPES or name in self.structs:
            self.curr_type = data_type
        else:
            self.error(f'invalid type "{name}"', data_type.type_name)
            
    
    def visit_var_def(self, var_def):
        var_def.data_type.accept(self)

       
        if self.symbol_table.exists_in_curr_env(var_def.var_name.lexeme):
            self.error('duplicate variable declared ' + var_def.var_name.lexeme, var_def.var_name)
        self.symbol_table.add(var_def.var_name.lexeme, self.curr_type)
        

        
    def visit_simple_term(self, simple_term):
        # TODO
        simple_term.rvalue.accept(self)
        
    
    def visit_complex_term(self, complex_term):
        # TODO
        complex_term.expr.accept(self)
        

    def visit_simple_rvalue(self, simple_rvalue):
        value = simple_rvalue.value
        line = simple_rvalue.value.line
        column = simple_rvalue.value.column
        type_token = None 
        if value.token_type == TokenType.INT_VAL:
            type_token = Token(TokenType.INT_TYPE, 'int', line, column)
        elif value.token_type == TokenType.DOUBLE_VAL:
            type_token = Token(TokenType.DOUBLE_TYPE, 'double', line, column)
        elif value.token_type == TokenType.STRING_VAL:
            type_token = Token(TokenType.STRING_TYPE, 'string', line, column)
        elif value.token_type == TokenType.BOOL_VAL:
            type_token = Token(TokenType.BOOL_TYPE, 'bool', line, column)
        elif value.token_type == TokenType.NULL_VAL:
            type_token = Token(TokenType.VOID_TYPE, 'void', line, column)
        self.curr_type = DataType(False, type_token)

        
    def visit_new_rvalue(self, new_rvalue):
        # TODO
        type_node = DataType(None, new_rvalue.type_name)
        if new_rvalue.type_name.lexeme not in BASE_TYPES and new_rvalue.array_expr == None:
            struct_def = self.structs[new_rvalue.type_name.lexeme]
            if(len(new_rvalue.struct_params) != len(struct_def.fields)):
                self.error('wrong amount of params in struct creation', new_rvalue.type_name)
        if new_rvalue.array_expr != None:
            type_node.is_array = True
        else:
            type_node.is_array = False
        
        
        if new_rvalue.struct_params != None:
            i = 0
            for expr in new_rvalue.struct_params:
                expr.accept(self)
                if self.curr_type.type_name.lexeme not in [struct_def.fields[i].data_type.type_name.lexeme, 'void']:
                    self.error('type error in struct creation params', new_rvalue.type_name)
                i = i+1


                

        self.curr_type = type_node
        
            
    def visit_var_rvalue(self, var_rvalue):
        # TODO
        
        type = DataType(None, None)

        if not self.symbol_table.exists(var_rvalue.path[0].var_name.lexeme):
            self.error(var_rvalue.path[0].var_name.lexeme + 'doesnt exist', var_rvalue.path[0].var_name)
        first_type = self.symbol_table.get(var_rvalue.path[0].var_name.lexeme)
        type.is_array = first_type.is_array
        type.type_name = first_type.type_name

        if type.is_array and var_rvalue.path[0].array_expr != None:
            type.is_array = False


        f_type = None
        i = 1
        l_len = len(var_rvalue.path)
        if first_type.type_name.lexeme not in BASE_TYPES:
            struct = self.structs[first_type.type_name.lexeme]
        while i < l_len:
            
            f_type = self.get_field_type(struct, var_rvalue.path[i].var_name.lexeme)
            if f_type == None:
                self.error('bad type name', var_rvalue.path[i].var_name)
            first_type = DataType(f_type.is_array, f_type.type_name)
            # 
            # if is array and no array expr and not last item in list
            if f_type.is_array and var_rvalue.path[i].array_expr == None and i < l_len-1:
                self.error('array type not indexed in middle of path', var_rvalue.path[i].var_name)
            # if array expr but not isarray
            if not f_type.is_array and var_rvalue.path[i].array_expr != None:
                self.error('trying to index non-array type', var_rvalue.path[i].var_name)
            # if array expr but not isarray
            
            if f_type.is_array and var_rvalue.path[i].array_expr != None:
                first_type.is_array = False
            
            i = i+1
            if i < len(var_rvalue.path):
                struct = self.structs[first_type.type_name.lexeme]

        if l_len > 1:
            type = first_type
     
        self.curr_type = type
            
        
