"""Implementation of the MyPL Virtual Machine (VM).

NAME: <Ryan St. Mary>
DATE: Spring 2024
CLASS: CPSC 326

"""

from mypl_error import *
from mypl_opcode import *
from mypl_frame import *


class VM:

    def __init__(self):
        """Creates a VM."""
        self.struct_heap = {}        # id -> dict
        self.array_heap = {}         # id -> list
        self.next_obj_id = 2024      # next available object id (int)
        self.frame_templates = {}    # function name -> VMFrameTemplate
        self.call_stack = []         # function call stack


       







    
    def __repr__(self):
        """Returns a string representation of frame templates."""
        s = ''
        for name, template in self.frame_templates.items():
            s += f'\nFrame {name}\n'
            for i in range(len(template.instructions)):
                s += f'  {i}: {template.instructions[i]}\n'
        return s
    
    def add_frame_template(self, template):
        """Add the new frame info to the VM. 

        Args: 
            frame -- The frame info to add.

        """
        self.frame_templates[template.function_name] = template

    
    def error(self, msg, frame=None):
        """Report a VM error."""
        if not frame:
            raise VMError(msg)
        pc = frame.pc - 1
        instr = frame.template.instructions[pc]
        name = frame.template.function_name
        msg += f' (in {name} at {pc}: {instr})'
        raise VMError(msg)

    
    #----------------------------------------------------------------------
    # RUN FUNCTION
    #----------------------------------------------------------------------
    
    def run(self, debug=False):
        """Run the virtual machine."""

        # grab the "main" function frame and instantiate it
        if not 'main' in self.frame_templates:
            self.error('No "main" functrion')
        frame = VMFrame(self.frame_templates['main'])
        self.call_stack.append(frame)

        # run loop (continue until run out of call frames or instructions)
        while self.call_stack and frame.pc < len(frame.template.instructions):
            # get the next instruction
            instr = frame.template.instructions[frame.pc]
            # increment the program count (pc)
            frame.pc += 1
            # for debugging:
            if debug:
                print('\n')
                print('\t FRAME.........:', frame.template.function_name)
                print('\t PC............:', frame.pc)
                print('\t INSTRUCTION...:', instr)
                val = None if not frame.operand_stack else frame.operand_stack[-1]
                print('\t NEXT OPERAND..:', val)
                cs = self.call_stack
                fun = cs[-1].template.function_name if cs else None
                print('\t NEXT FUNCTION..:', fun)

            #------------------------------------------------------------
            # Literals and Variables
            #------------------------------------------------------------

            if instr.opcode == OpCode.PUSH:
                frame.operand_stack.append(instr.operand)

            elif instr.opcode == OpCode.POP:
                frame.operand_stack.pop()

            elif instr.opcode == OpCode.STORE:
                if instr.operand == len(frame.variables):
                    frame.variables.append(frame.operand_stack.pop())
                else:
                    frame.variables[instr.operand] = frame.operand_stack.pop()
            
            elif instr.opcode == OpCode.LOAD:
                frame.operand_stack.append(frame.variables[instr.operand])
            #------------------------------------------------------------
            # Operations
            #------------------------------------------------------------
            # TODO: Fill in rest of ops
                

            elif instr.opcode == OpCode.ADD:
                x = frame.operand_stack.pop()
                y = frame.operand_stack.pop()

                if None in [x, y]:
                    self.error('null in add', frame)

                frame.operand_stack.append(y+x)
            
            elif instr.opcode == OpCode.SUB:
                x = frame.operand_stack.pop()
                y = frame.operand_stack.pop()

                if None in [x, y]:
                    self.error('null in sub', frame)

                frame.operand_stack.append(y-x)
            
            elif instr.opcode == OpCode.MUL:
                x = frame.operand_stack.pop()
                y = frame.operand_stack.pop()

                if None in [x, y]:
                    self.error('null in mul', frame)

                frame.operand_stack.append(y*x)
            
            elif instr.opcode == OpCode.DIV:
                x = frame.operand_stack.pop()
                y = frame.operand_stack.pop()

                if x in [0, 0.0]:
                    self.error('Divide by 0 error', frame)
                
                if None in [x, y]:
                    self.error('null in div', frame)

                result = y/x

                

                if type(x) is int:
                    result = int(result)

                frame.operand_stack.append(result)

            elif instr.opcode == OpCode.CMPEQ:
                x = frame.operand_stack.pop()
                y = frame.operand_stack.pop()

                

                result = y == x
                frame.operand_stack.append(result)
            
            elif instr.opcode == OpCode.CMPLE:
                x = frame.operand_stack.pop()
                y = frame.operand_stack.pop()

                if None in [x, y]:
                    self.error('null in cmple', frame)
                
                result = y <= x
                frame.operand_stack.append(result)
            
            elif instr.opcode == OpCode.CMPLT:
                x = frame.operand_stack.pop()
                y = frame.operand_stack.pop()

                if None in [x, y]:
                    self.error('null in cmplt', frame)

                result = y < x
                frame.operand_stack.append(result)
            
            elif instr.opcode == OpCode.CMPNE:
                x = frame.operand_stack.pop()
                y = frame.operand_stack.pop()

               
                
                result = y != x
                frame.operand_stack.append(result)

            elif instr.opcode == OpCode.AND:
                x = frame.operand_stack.pop()
                y = frame.operand_stack.pop()

                if None in [x, y]:
                    self.error('null in and', frame)

                result = y and x
                frame.operand_stack.append(result)

            elif instr.opcode == OpCode.OR:
                x = frame.operand_stack.pop()
                y = frame.operand_stack.pop()

                if None in [x, y]:
                    self.error('null in or', frame)

                frame.operand_stack.append(y or x)

            elif instr.opcode == OpCode.NOT:
                x = frame.operand_stack.pop()

                if x is None:
                    self.error('null in not', frame)

                frame.operand_stack.append(not x)
            
            
            
            
            
            

            #------------------------------------------------------------
            # Branching
            #------------------------------------------------------------

            # TODO: Fill in rest of ops
            elif instr.opcode == OpCode.JMP:
                frame.pc = instr.operand

            elif instr.opcode == OpCode.JMPF:
                if frame.operand_stack.pop() == False:
                    frame.pc = instr.operand  
            #------------------------------------------------------------
            # Functions
            #------------------------------------------------------------
            

            elif instr.opcode == OpCode.CALL:
                f = VMFrame(self.frame_templates[instr.operand])
                self.call_stack.append(f)
                # pop arguments from op stack, push to f operand stack
                for x in range(f.template.arg_count):
                    f.operand_stack.append(frame.operand_stack.pop())
                # make f frame
                frame = f

            elif instr.opcode == OpCode.RET:
                r_val = frame.operand_stack.pop()
                self.call_stack.pop()

                if len(self.call_stack) > 0:
                    frame = self.call_stack[-1]
                    frame.operand_stack.append(r_val)


            
            #------------------------------------------------------------
            # Built-In Functions
            #------------------------------------------------------------
          
            # TODO: Fill in rest of ops
            elif instr.opcode == OpCode.WRITE:
                x = frame.operand_stack.pop()
                if x is None:
                    x = 'null'
                if type(x) is bool:
                    x = str(x).lower()
                print(x, end = '')
            
            elif instr.opcode == OpCode.READ:
                frame.operand_stack.append(input())

            elif instr.opcode == OpCode.LEN:
                x = frame.operand_stack.pop()

                if x is None:
                    self.error('null has no length', frame)
                
                if type(x) is str:
                    l = len(x)
                else:
                    l = len(self.array_heap[x])
                
                
                frame.operand_stack.append(l)

          

            elif instr.opcode == OpCode.GETC:
                # x = index, y = string
                x = frame.operand_stack.pop()
                y = frame.operand_stack.pop()
                
                if None in [x,y]:
                    self.error('null in array access', frame)
                
                if y > len(x)-1 or y < 0:
                    self.error('bad index', frame)

                val = x[y]

                frame.operand_stack.append(val)

            elif instr.opcode == OpCode.TOINT:
                x = frame.operand_stack.pop()
                try:
                    x = int(x)
                except ValueError:
                    self.error('bad int in cast', frame)
                except TypeError:
                    self.error('bad int in cast', frame)
                

                frame.operand_stack.append(x)

            elif instr.opcode == OpCode.TODBL:
                x = frame.operand_stack.pop()
                try:
                    x = float(x)
                except ValueError:
                    self.error('bad double in cast', frame)
                except TypeError:
                    self.error('bad double in cast', frame)
                
                frame.operand_stack.append(x)

            elif instr.opcode == OpCode.TOSTR:
                x = frame.operand_stack.pop()
                if x is None:
                    self.error('null in tostring', frame)
                x = str(x)

                frame.operand_stack.append(x)
            
            #------------------------------------------------------------
            # Heap
            #------------------------------------------------------------


            # TODO: Fill in rest of ops
            elif instr.opcode == OpCode.ALLOCA:
                size = frame.operand_stack.pop()

                if type(size) is not int:
                    self.error('array size must be int', frame)
                
                if size < 0:
                    self.error('size can\'t be negative', frame)

                list = [None for _ in range(size)]

                self.array_heap[self.next_obj_id] = list
                frame.operand_stack.append(self.next_obj_id)
                self.next_obj_id = self.next_obj_id + 1

                


            elif instr.opcode == OpCode.GETI:
                # pop index x, pop oid y, push obj(y)[x] onto stack
                x = frame.operand_stack.pop()
                y = frame.operand_stack.pop()

                
                if None in [x, y]:
                    self.error('indicies can\'t be null', frame)
                
               
                if x >= len(self.array_heap[y]) or x < 0:
                    self.error('bad array index')

               

                val = self.array_heap[y][x]
                frame.operand_stack.append(val)
               

            elif instr.opcode == OpCode.SETI:
                # pop value x, pop index y, pop oid z, set array obj(z)[y] = x
                x = frame.operand_stack.pop()
                y = frame.operand_stack.pop()
                z = frame.operand_stack.pop()



                if None in [y, z]:
                    self.error('indicies can\'t be null', frame)
                
                if y < 0 or y >= len(self.array_heap[z]):
                    self.error('bad index', frame)


                self.array_heap[z][y] = x
           
            
            elif instr.opcode == OpCode.ALLOCS:
                self.struct_heap[self.next_obj_id] = {}

                frame.operand_stack.append(self.next_obj_id)
                self.next_obj_id = self.next_obj_id + 1

                

            elif instr.opcode == OpCode.GETF:
                # pop oid x, push obj(x)[A] onto stack
                x = frame.operand_stack.pop()
                
                if x is None:
                    self.error('bad head index', frame)

                val = self.struct_heap[x][instr.operand]
                frame.operand_stack.append(val)
          

            elif instr.opcode == OpCode.SETF:
                # pop value x, pop oid y, set obj(y)[A] = x
                x = frame.operand_stack.pop()
                y = frame.operand_stack.pop()

                if y is None:
                    self.error('bad heap index', frame)

                self.struct_heap[y][instr.operand] = x
          
            
            #------------------------------------------------------------
            # Special 
            #------------------------------------------------------------

            elif instr.opcode == OpCode.DUP:
                x = frame.operand_stack.pop()
                frame.operand_stack.append(x)
                frame.operand_stack.append(x)

            elif instr.opcode == OpCode.NOP:
                # do nothing
                pass

            else:
                self.error(f'unsupported operation {instr}')
