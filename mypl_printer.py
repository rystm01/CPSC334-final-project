"""Print Visitor for pretty printing a MyPL program.

NAME: <your name here>
DATE: Spring 2024
CLASS: CPSC 326

"""

from dataclasses import dataclass
from mypl_token import Token, TokenType
from mypl_ast import *


class PrintVisitor(Visitor):
    """Visitor implementation to pretty print MyPL program."""

    def __init__(self):
        self.indent = 0

    # Helper Functions
        
    def output(self, msg):
        """Prints message without ending newline.

        Args:
           msg -- The string to print.

        """
        print(msg, end='')

        
    def output_indent(self):
        """Prints an initial indent string."""
        self.output('  ' * self.indent)


    def output_semicolon(self, stmt):
        """Prints a semicolon if the type of statment should end in a
        semicolon.
        
        Args:
            stmt -- The statement to print a semicolon after.

        """
        if type(stmt) in [VarDecl, AssignStmt, ReturnStmt, CallExpr]:
            self.output(';')

    # Visitor Functions
    
    def visit_program(self, program):
        for struct in program.struct_defs:
            struct.accept(self)
            self.output('\n')
        for fun in program.fun_defs:
            fun.accept(self)
            self.output('\n')            

            
    def visit_struct_def(self, struct_def):
        self.output('struct ' + struct_def.struct_name.lexeme + ' {\n')
        self.indent += 1
        for var_def in struct_def.fields:
            self.output_indent()
            var_def.accept(self)
            self.output(';\n')
        self.indent -= 1
        self.output('}\n')


    def visit_fun_def(self, fun_def):
        fun_def.return_type.accept(self)
        self.output(' ' + fun_def.fun_name.lexeme + '(')
        for i in range(len(fun_def.params)):
            fun_def.params[i].accept(self)
            if i < len(fun_def.params) - 1:
                self.output(', ')
        self.output(') {\n')
        self.indent += 1
        for stmt in fun_def.stmts:
            self.output_indent()
            stmt.accept(self)
            self.output_semicolon(stmt)
            self.output('\n')
        self.indent -= 1
        self.output('}\n')


    # TODO: Finish the rest of the visitor functions below

    def visit_expr(self, expr):
        if(expr.not_op):
            self.output('not (')
        expr.first.accept(self)
        if expr.op != None:
            self.output(' ' + expr.op.lexeme + ' ') 
        if(expr.rest != None):
            expr.rest.accept(self)
        if expr.not_op:
            self.output(')')
    
    def visit_if_stmt(self, if_stmt):
        self.output('if (')
        if_stmt.if_part.condition.accept(self)
        self.output(') {\n')
        self.indent+=1
        for stmt in if_stmt.if_part.stmts:
            self.output_indent()
            stmt.accept(self)
            self.output_semicolon(stmt)
            self.output('\n')
        self.indent-=1
        self.output_indent()
        self.output('}')
        if if_stmt.else_ifs != [] or if_stmt.else_stmts != []:
            self.output('\n')
        
        for else_if in if_stmt.else_ifs:
            self.output_indent()
            self.output('elseif (')
            
            else_if.condition.accept(self)
            self.output(') {\n')
            self.indent +=1
            for stmt in else_if.stmts:
                self.output_indent()
                stmt.accept(self)
                self.output_semicolon(stmt)
                self.output('\n')
            self.indent-=1
            self.output_indent()
            self.output('}\n')
        if len(if_stmt.else_stmts) > 0:
            self.output_indent()
            self.output('else {\n')
            self.indent+=1
            for stmt in if_stmt.else_stmts:
                self.output_indent()
                stmt.accept(self)
                self.output_semicolon(stmt)
                self.output('\n')
            self.indent-=1
            self.output_indent()
            self.output('}')
    
    def visit_return_stmt(self, return_stmt):
        
        self.output('return ')
        return_stmt.expr.accept(self)

    def visit_var_decl(self, var_decl):
        var_decl.var_def.accept(self)
        self.output(' = ')
        var_decl.expr.accept(self)

    def visit_assign_stmt(self, assign_stmt):
        path_len = len(assign_stmt.lvalue)
        i = 0
        for var_ref in assign_stmt.lvalue:
            self.output(var_ref.var_name.lexeme)
            if(var_ref.array_expr != None):
                self.output('[') 
                var_ref.array_expr.accept(self)
                self.output(']')
            if i < path_len-1 and path_len!=1:
                self.output('.')
            i = i+1
        self.output(' = ')
        assign_stmt.expr.accept(self)
        

    def visit_while_stmt(self, while_stmt):
        self.output('while (')
        while_stmt.condition.accept(self)
        self.output(') {\n')
        self.indent+=1
        for stmt in while_stmt.stmts:
            self.output_indent()
            stmt.accept(self)
            self.output_semicolon(stmt)
            self.output('\n')
        self.indent-=1
        self.output_indent()
        self.output('}')

    def visit_for_stmt(self, for_stmt):
        self.output('for (')
        for_stmt.var_decl.accept(self)
        self.output('; ')
        for_stmt.condition.accept(self)
        self.output('; ')
        for_stmt.assign_stmt.accept(self)
        self.output(') {\n')
        self.indent+=1
        for stmt in for_stmt.stmts:
            self.output_indent()
            stmt.accept(self)
            self.output_semicolon(stmt)
            self.output('\n')
        self.indent -= 1
        self.output_indent()
        self.output('}')


    def visit_call_expr(self, call_expr):
        self.output(call_expr.fun_name.lexeme + '(')
        for i in range(len(call_expr.args)):
            call_expr.args[i].accept(self)
            if i < len(call_expr.args) - 1:
                self.output(', ')
        self.output(')')
    
    
    def visit_data_type(self, data_type):
        if data_type.is_array:
            self.output('array ')
        self.output(data_type.type_name.lexeme)

    def visit_var_def(self, var_def):
        var_def.data_type.accept(self)
        self.output(' ' + var_def.var_name.lexeme)

    def visit_simple_term(self, simple_term):
        simple_term.rvalue.accept(self)

    def visit_complex_term(self, complex_term):
        self.output('(')
        complex_term.expr.accept(self)
        self.output(')')

    def visit_simple_rvalue(self, simple_rvalue):
        if(simple_rvalue.value.token_type == TokenType.STRING_VAL):
            self.output("\"" + simple_rvalue.value.lexeme + "\"")
        else:
            self.output(simple_rvalue.value.lexeme)
    
    def visit_new_rvalue(self, new_rvalue):
        self.output('new ' + new_rvalue.type_name.lexeme)
        if new_rvalue.array_expr != None:
            self.output('[')
            new_rvalue.array_expr.accept(self)
            self.output(']')
        self.output('(')
        for i in range( len(new_rvalue.struct_params)):
            new_rvalue.struct_params[i].accept(self)
            if i < len(new_rvalue.struct_params) - 1:
                self.output(', ')
        self.output(')')

    def visit_var_rvalue(self, var_rvalue):
        path_len = len(var_rvalue.path)
        i = 0
        for var_ref in var_rvalue.path:
            self.output(var_ref.var_name.lexeme)
            if var_ref.array_expr != None:
                self.output('[')
                var_ref.array_expr.accept(self)
                self.output(']')
            if i < path_len-1 and path_len!=1:
                self.output('.')
            i = i+1

        
