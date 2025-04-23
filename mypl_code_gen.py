"""IR code generator for converting MyPL to VM Instructions. 

NAME: <Ryan St Mary>
DATE: Spring 2024
CLASS: CPSC 326

"""

from mypl_token import *
from mypl_ast import *
from mypl_var_table import *
from mypl_frame import *
from mypl_opcode import *
from mypl_vm import *


class CodeGenerator (Visitor):

    def __init__(self, vm):
        """Creates a new Code Generator given a VM. 
        
        Args:
            vm -- The target vm.
        """
        # the vm to add frames to
        self.vm = vm
        # the current frame template being generated
        self.curr_template = None
        # for var -> index mappings wrt to environments
        self.var_table = VarTable()
        # struct name -> StructDef for struct field info
        self.struct_defs = {}

    
    def add_instr(self, instr):
        """Helper function to add an instruction to the current template."""
        self.curr_template.instructions.append(instr)

        
    def visit_program(self, program):
        for struct_def in program.struct_defs:
            struct_def.accept(self)
        for fun_def in program.fun_defs:
            fun_def.accept(self)

    
    def visit_struct_def(self, struct_def):
        # remember the struct def for later
        self.struct_defs[struct_def.struct_name.lexeme] = struct_def

        
    def visit_fun_def(self, fun_def):
        # TODO
        
        frame = VMFrameTemplate(fun_def.fun_name.lexeme, len(fun_def.params), [])
        self.curr_template = frame

        self.var_table.push_environment()
        
        for param in fun_def.params:
            self.var_table.add(param.var_name.lexeme)
            index = self.var_table.get(param.var_name.lexeme)
            self.add_instr(STORE(index))
        
        for stmt in fun_def.stmts:
            stmt.accept(self)
        
        if fun_def.stmts == []  or type(fun_def.stmts[-1]) != ReturnStmt:
            self.add_instr(PUSH(None))
            self.add_instr(RET())
        


        self.var_table.pop_environment()

        self.vm.add_frame_template(frame)

     
        

        

    
    def visit_return_stmt(self, return_stmt):
        # TODO

        # expr puts val on stack
        return_stmt.expr.accept(self)
        self.add_instr(RET())

        
    def visit_var_decl(self, var_decl):
        # TODO

        # add var name, evaluate
        var_name = var_decl.var_def.var_name.lexeme
        self.var_table.add(var_name)
        if var_decl.expr != None:
            var_decl.expr.accept(self)
        else:
            self.add_instr(PUSH(None))

        # store
        index = self.var_table.get(var_name)
        self.add_instr(STORE(index))


    
    def visit_assign_stmt(self, assign_stmt):
        # TODO
        index = self.var_table.get(assign_stmt.lvalue[0].var_name.lexeme)
        self.add_instr(LOAD(index))
       

        if len(assign_stmt.lvalue) > 1 :
            
            # if array index on first var
            if assign_stmt.lvalue[0].array_expr != None:
                assign_stmt.lvalue[0].array_expr.accept(self)
                
                self.add_instr(GETI())
            
            # iterate over path
            i = 1
            while i < len(assign_stmt.lvalue) - 1:
                self.add_instr(GETF(assign_stmt.lvalue[i].var_name.lexeme))
                

                # if array index in middle
                if assign_stmt.lvalue[i].array_expr != None:
                    assign_stmt.lvalue[i].array_expr.accept(self)
                    self.add_instr(GETI())
                    
                i = i + 1
            
            # path ends in array
            if assign_stmt.lvalue[i].array_expr != None:
                self.add_instr(GETF(assign_stmt.lvalue[i].var_name.lexeme))
                assign_stmt.lvalue[i].array_expr.accept(self)
                assign_stmt.expr.accept(self)
                self.add_instr(SETI())
        
            # path doesnt end with array
            else:
                assign_stmt.expr.accept(self)
                self.add_instr(SETF(assign_stmt.lvalue[i].var_name.lexeme))
       
        # single var case
        if len(assign_stmt.lvalue) == 1:
           
            if assign_stmt.lvalue[0].array_expr == None:
                assign_stmt.expr.accept(self)
                self.add_instr(STORE(index))
            else:
                
                assign_stmt.lvalue[0].array_expr.accept(self)
                assign_stmt.expr.accept(self)
                self.add_instr(SETI())
                





    
    def visit_while_stmt(self, while_stmt):
        # TODO
        
        # place to jump to before condition
        start = len(self.curr_template.instructions)
        while_stmt.condition.accept(self)
        self.var_table.push_environment()

        instr_idx = len(self.curr_template.instructions)
        jump_instr = JMPF(-1)
        self.add_instr(jump_instr) 

        for stmt in while_stmt.stmts:
            stmt.accept(self)
        
        
        self.add_instr(JMP(start))
        self.curr_template.instructions[instr_idx] = JMPF(len(self.curr_template.instructions))
        self.add_instr(NOP())

        self.var_table.pop_environment()

        
    def visit_for_stmt(self, for_stmt):
        # TODO
        self.var_table.push_environment()

        for_stmt.var_decl.accept(self)

        start = len(self.curr_template.instructions)
        for_stmt.condition.accept(self)
        

        instr_idx = len(self.curr_template.instructions)
        self.add_instr(JMPF(-1))

        for stmt in for_stmt.stmts:
            stmt.accept(self)

        for_stmt.assign_stmt.accept(self)
        
        self.var_table.pop_environment()
        
        self.add_instr(JMP(start))
        
        self.curr_template.instructions[instr_idx] = JMPF(len(self.curr_template.instructions))
        self.add_instr(NOP())

        

    
    def visit_if_stmt(self, if_stmt):
        # TODO
        jmp_idxs = []
        jmpf_idxs = []
        jmpf_to = []
        

        # first if
        if_stmt.if_part.condition.accept(self)
        jmpf_idxs.append(len(self.curr_template.instructions))
        self.add_instr(JMPF(-1))
        for stmt in if_stmt.if_part.stmts:
            stmt.accept(self)
        jmp_idxs.append(len(self.curr_template.instructions))
        self.add_instr(JMP(-1))
        jmpf_to.append(len(self.curr_template.instructions))


        # else if s
        for else_if in if_stmt.else_ifs:
            
            else_if.condition.accept(self)
            
            jmpf_idxs.append(len(self.curr_template.instructions))
            self.add_instr(JMPF(-1))
            for stmt in else_if.stmts:
                stmt.accept(self)
            jmp_idxs.append(len(self.curr_template.instructions))
            self.add_instr(JMP(-1))
            jmpf_to.append(len(self.curr_template.instructions))

        
        
        # elses
        for stmt in if_stmt.else_stmts:
            stmt.accept(self)
        
        

       # end of if stmts
        self.add_instr(NOP())
        for i in jmp_idxs:
            self.curr_template.instructions[i] = JMP(len(self.curr_template.instructions)-1)
        
        
        
        for i in range (len(jmpf_idxs)):
            self.curr_template.instructions[jmpf_idxs[i]] = JMPF(jmpf_to[i])
        
            
    
    def visit_call_expr(self, call_expr):
        # TODO
        for arg in call_expr.args:
            arg.accept(self)
        if call_expr.fun_name.lexeme == "print":
            self.add_instr(WRITE())
        elif call_expr.fun_name.lexeme == "itos":
            self.add_instr(TOSTR())
        elif call_expr.fun_name.lexeme == "stoi":
            self.add_instr(TOINT())
        elif call_expr.fun_name.lexeme == "dtoi":
            self.add_instr(TOINT())
        elif call_expr.fun_name.lexeme == "dtos":
            self.add_instr(TOSTR())
        elif call_expr.fun_name.lexeme == "stod":
            self.add_instr(TODBL())
        elif call_expr.fun_name.lexeme == "itod":
             self.add_instr(TODBL())
        elif call_expr.fun_name.lexeme == "length":
            self.add_instr(LEN())
        elif call_expr.fun_name.lexeme == "get":
            self.add_instr(GETC())
        elif call_expr.fun_name.lexeme == "input":
            self.add_instr(READ())
        else:
            self.add_instr(CALL(call_expr.fun_name.lexeme))

        
    def visit_expr(self, expr):
        # TODO
        

        
        # accept things(resolve to one value on operand stack) then add operand
        if expr.op != None:
            if expr.op.token_type == TokenType.AND:
                expr.first.accept(self)
                expr.rest.accept(self)
                self.add_instr(AND())
            elif expr.op.token_type == TokenType.OR:
                expr.first.accept(self)
                expr.rest.accept(self)
                self.add_instr(OR())
            elif expr.op.token_type == TokenType.LESS:
                expr.first.accept(self)
                expr.rest.accept(self)
                self.add_instr(CMPLT())
            elif expr.op.token_type == TokenType.LESS_EQ:
                expr.first.accept(self)
                expr.rest.accept(self)
                self.add_instr(CMPLE())
            elif expr.op.token_type == TokenType.GREATER:
                expr.rest.accept(self)
                expr.first.accept(self)
                self.add_instr(CMPLT())
            elif expr.op.token_type == TokenType.GREATER_EQ:
                expr.rest.accept(self)
                expr.first.accept(self)
                self.add_instr(CMPLE())
            elif expr.op.token_type == TokenType.EQUAL:
                expr.first.accept(self)
                expr.rest.accept(self)
                self.add_instr(CMPEQ())
            elif expr.op.token_type == TokenType.NOT_EQUAL:
                expr.first.accept(self)
                expr.rest.accept(self)
                self.add_instr(CMPEQ())
                self.add_instr(NOT())
            elif expr.op.token_type == TokenType.PLUS:
                expr.first.accept(self)
                expr.rest.accept(self)
                self.add_instr(ADD())
            elif expr.op.token_type == TokenType.MINUS:
                expr.first.accept(self)
                expr.rest.accept(self)
                self.add_instr(SUB())
            elif expr.op.token_type == TokenType.DIVIDE:
                expr.first.accept(self)
                expr.rest.accept(self)
                self.add_instr(DIV())
            elif expr.op.token_type == TokenType.TIMES:
                expr.first.accept(self)
                expr.rest.accept(self)
                self.add_instr(MUL())
            
        # simple expr case
        else:
            expr.first.accept(self)

            
        # not case+
        if expr.not_op == True:
            self.add_instr(NOT())
            
    def visit_data_type(self, data_type):
        # nothing to do here
        pass

    
    def visit_var_def(self, var_def):
        # nothing to do here
        pass

    
    def visit_simple_term(self, simple_term):
        simple_term.rvalue.accept(self)

        
    def visit_complex_term(self, complex_term):
        complex_term.expr.accept(self)

        
    def visit_simple_rvalue(self, simple_rvalue):
        val = simple_rvalue.value.lexeme
        if simple_rvalue.value.token_type == TokenType.INT_VAL:
            self.add_instr(PUSH(int(val)))
        elif simple_rvalue.value.token_type == TokenType.DOUBLE_VAL:
            self.add_instr(PUSH(float(val)))
        elif simple_rvalue.value.token_type == TokenType.STRING_VAL:
            val = val.replace('\\n', '\n')
            val = val.replace('\\t', '\t')
            self.add_instr(PUSH(val))
        elif val == 'true':
            self.add_instr(PUSH(True))
        elif val == 'false':
            self.add_instr(PUSH(False))
        elif val == 'null':
            self.add_instr(PUSH(None))

    
    def visit_new_rvalue(self, new_rvalue):
        # TODO
        # struct case
        i = 0
        if new_rvalue.array_expr == None:
            self.add_instr(ALLOCS())
            for param in new_rvalue.struct_params:
                self.add_instr(DUP())
                param.accept(self)
                self.add_instr(SETF(self.struct_defs[new_rvalue.type_name.lexeme].fields[i].var_name.lexeme))
                i = i+1

        # array case
        else:
            new_rvalue.array_expr.accept(self)
            self.add_instr(ALLOCA())



    
    def visit_var_rvalue(self, var_rvalue):
        # TODO
        index = self.var_table.get(var_rvalue.path[0].var_name.lexeme)
        self.add_instr(LOAD(index))
        if var_rvalue.path[0].array_expr != None:
            var_rvalue.path[0].array_expr.accept(self)
            self.add_instr(GETI())
        i = 1
        # struct = self.struct_defs[var_rvalue.path[0].var_name.lexeme]
        while (i < len(var_rvalue.path)):
            # self.add_instr(LOAD(index))
            self.add_instr(GETF(var_rvalue.path[i].var_name.lexeme))
           
            if var_rvalue.path[i].array_expr != None:
                var_rvalue.path[i].array_expr.accept(self)
                self.add_instr(GETI())

            i = i+1


        
                
