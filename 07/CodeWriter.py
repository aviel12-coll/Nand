"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class CodeWriter:
    """Translates VM commands into Hack assembly code."""

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Initializes the CodeWriter.

        Args:
            output_stream (typing.TextIO): output stream.
        """
        self.output_stream = output_stream
        self.filename = ""
        self.label_counter = 0

    def set_file_name(self, filename: str) -> None:
        """Informs the code writer that the translation of a new VM file is 
        started.

        Args:
            filename (str): The name of the VM file.
        """
        # Your code goes here!
        # This function is useful when translating code that handles the
        # static segment. For example, in order to prevent collisions between two
        # .vm files which push/pop to the static segment, one can use the current
        # file's name in the assembly variable's name and thus differentiate between
        # static variables belonging to different files.
        # To avoid problems with Linux/Windows/MacOS differences with regards
        # to filenames and paths, you are advised to parse the filename in
        # the function "translate_file" in Main.py using python's os library,
        # For example, using code similar to:
        # input_filename, input_extension = os.path.splitext(os.path.basename(input_file.name))
        self.filename = filename   

    def write_arithmetic(self, command: str) -> None:
        """Writes assembly code that is the translation of the given 
        arithmetic command. For the commands eq, lt, gt, you should correctly
        compare between all numbers our computer supports, and we define the
        value "true" to be -1, and "false" to be 0.

        Args:
            command (str): an arithmetic command.
        """
        if command == "not":
            self.write_not()
        if command == "neg":
            self.write_neg()
        if command == "add":
            self.write_add()
        if command == "sub":
            self.write_sub()

        if command == "eq":
            self.write_eq()
        if command == "gt":
            self.write_gt() 
        if command == "lt":
            self.write_lt()
        if command == "and":
            self.write_and()

        if command == "or":
            self.write_or()      

    def write_lt(self) -> None:
        """Writes assembly code that is the translation of the 'lt' command.
        The 'lt' command pops the top two values from the stack, compares them
        and pushes 'true' (-1) onto the stack if the first is less than the second,
        or 'false' (0) if it is not.
        """
        label_true = f"LT_TRUE_{self.label_counter}"
        label_end = f"LT_END_{self.label_counter}"
        self.label_counter += 1

        self.output_stream.write(
            "// lt\n"
            "@SP\n"
            "A=M-1\n"    # A=SP-1
            "M=M-1\n"    # SP--
            "D=M\n"      # D=Y  
            "A=A-1\n"    # A=SP-2
            "D=M-D\n"    # D=X-Y
            f"@{label_true}\n"
            "D;JLT\n"    # If X<Y, jump to label_true
            "@SP\n"
            "A=M-1\n"
            "A=A-1\n"
            "M=0\n"      # Push false (0)
            f"@{label_end}\n"
            "0;JMP\n"
            f"({label_true})\n"
            "@SP\n"
            "A=M-1\n"
            "A=A-1\n"
            "M=-1\n"     # Push true (-1)
            f"({label_end})\n"
        )


    def write_and(self) -> None:
        """Writes assembly code that is the translation of the 'and' command.
        The 'and' command pops the top two values from the stack, computes their
        bitwise AND, and pushes the result back onto the stack.
        """
        self.output_stream.write(
            "// and\n"
            "@SP\n"
            "A=M-1\n"    # A=SP-1
            "M=M-1\n"    # SP--
            "D=M\n"      # D=Y  
            "A=A-1\n"    # A=SP-2
            "M=M&D\n"    # M=X&Y
        )
    def write_or(self) -> None:
        """Writes assembly code that is the translation of the 'or' command.
        The 'or' command pops the top two values from the stack, computes their
        bitwise OR, and pushes the result back onto the stack.
        """
        self.output_stream.write(
            "// or\n"
            "@SP\n"
            "A=M-1\n"    # A=SP-1
            "M=M-1\n"    # SP--
            "D=M\n"      # D=Y  
            "A=A-1\n"    # A=SP-2
            "M=M|D\n"    # M=X|Y
        )
    def write_eq(self) -> None:
        """Writes assembly code that is the translation of the 'eq' command.
        The 'eq' command pops the topmost value from the stack, checks if it equals 0,
        and pushes 'true' (-1) onto the stack if it is 0, or 'false' (0) if it is not.
        """
        label_true = f"EQ_TRUE_{self.label_counter}"
        label_end = f"EQ_END_{self.label_counter}"
        self.label_counter += 1

        self.output_stream.write(
            "// eq\n"
            "@SP\n"
            "A=M-1\n"    # A=SP-1
            "D=M\n"      # D=X (top value)
            f"@{label_true}\n"
            "D;JEQ\n"    # If X==0, jump to label_true
            "@SP\n"
            "A=M-1\n"    # A=SP-1
            "M=0\n"      # Push false (0)
            f"@{label_end}\n"
            "0;JMP\n"
            f"({label_true})\n"
            "@SP\n"
            "A=M-1\n"    # A=SP-1
            "M=-1\n"     # Push true (-1)
            f"({label_end})\n"
        )          

    def  write_sub(self) -> None:
        """Writes assembly code that is the translation of the 'sub' command.
        The 'sub' command pops the top two values from the stack, computes their
        difference (topmost minus the one below it), and pushes the result back onto the stack.
        """
        self.output_stream.write(
            "// sub\n"
            "@SP\n"
            "A=M-1\n"    # A=SP-1
            "M=M-1\n"    # SP--
            "D=M\n"      # D=Y  
            "A=A-1\n"    # A=SP-2
            "M=M-D\n"    # M=X-Y
        )   



       


    def write_add(self) -> None:
        """Writes assembly code that is the translation of the 'add' command.
        The 'add' command pops the top two values from the stack, computes their
        sum, and pushes the result back onto the stack.
        """
        self.output_stream.write(
            "// add\n"
            "@SP\n"
            "A=M-1\n"    # A=SP-1
            "M=M-1\n"    # SP--
            "D=M\n"      # D=Y  
            "A=A-1\n"    # A=SP-2
            "M=M+D\n"    # M=X+Y
        )

    # handle the 'not' command
    def write_not(self) -> None:
        """Writes assembly code that is the translation of the 'not' command.
        The 'not' command pops the topmost value from the stack, computes its
        bitwise negation, and pushes the result back onto the stack.
        """
        self.output_stream.write(

            "// not\n"
            "@SP\n"
            "A=M-1\n"   # Point to the topmost value
            "M=!M\n"    # Compute bitwise negation
        ) 
    def write_neg(self) -> None:
        """Writes assembly code that is the translation of the 'neg' command.
        The 'neg' command pops the topmost value from the stack, computes its
        arithmetic negation, and pushes the result back onto the stack.
        """
        self.output_stream.write(

            "// neg\n"
            "@SP\n"
            "A=M-1\n"   # Point to the topmost value
            "M=-M\n"    # Compute arithmetic negation
        )

        
        

    def write_push_pop(self, command: str, segment: str, index: int) -> None:
        """Writes assembly code that is the translation of the given 
        command, where command is either C_PUSH or C_POP.

        Args:
            command (str): "C_PUSH" or "C_POP".
            segment (str): the memory segment to operate on.
            index (int): the index in the memory segment.
        """
        # Your code goes here!
        # Note: each reference to "static i" appearing in the file Xxx.vm should
        # be translated to the assembly symbol "Xxx.i". In the subsequent
        # assembly process, the Hack assembler will allocate these symbolic
        # variables to the RAM, starting at address 16.
        
        if command == "C_PUSH" and segment == "constant":
            self.write_push_constant(index)
            return

        if command == "C_PUSH" and segment in ("local", "argument", "this", "that"):
            base_map = {
                "local": "LCL",
                "argument": "ARG",
                "this": "THIS",
                "that": "THAT"
            }
            self.write_pust_base(base_map[segment], index)
            return

        if command == "C_POP" and segment in ("local", "argument", "this", "that"):
            base_map = {
                "local": "LCL",
                "argument": "ARG",
                "this": "THIS",
                "that": "THAT"
            }
            self.write_pop_base(base_map[segment], index)
            return

        if command == "C_PUSH" and segment == "temp":
            self.write_push_temp(index)
            return

        if command == "C_POP" and segment == "temp":
            self.write_pop_temp(index)
            return

        if command == "C_PUSH" and segment == "pointer":
            self.write_push_pointer(index)
            return

        if command == "C_POP" and segment == "pointer":
            self.write_pop_pointer(index)
            return
    
    # consst not pointing to ram   
    def write_push_constant(self, index: int) -> None:
        """Writes assembly code for 'push constant index'."""
        self.output_stream.write(
            f"// push constant {index}\n"
            f"@{index}\n"
            "D=A\n"          # D = constant value
            "@SP\n"
            "A=M\n"          # A = SP (top free slot)
            "M=D\n"          # *SP = D
            "@SP\n"
            "M=M+1\n" )  
                 
    def write_push_local(self, index: int) -> None:
        """Writes assembly code for 'push local index'."""
        self.output_stream.write(
            f"// push local {index}\n"
            "@LCL\n"
            "D=M\n"              # D = base address of local segment
            f"@{index}\n"
            "A=D+A\n"            # A = LCL + index
            "D=M\n"              # D = RAM[LCL + index]
            "@SP\n"
            "A=M\n"              # A = SP (first free stack slot)
            "M=D\n"              # *SP = value
            "@SP\n"
            "M=M+1\n"            # SP++
        )


    def write_pop_local(self, index: int) -> None:
        """Writes assembly code for 'pop local index'."""
        self.output_stream.write(
            f"// pop local {index}\n"
            "@LCL\n"
            "D=M\n"              # D = base address of local segment
            f"@{index}\n"
            "D=D+A\n"            # D = LCL + index
            "@R13\n"
            "M=D\n"              # R13 = target address
            "@SP\n"
            "AM=M-1\n"           # SP--; A = SP
            "D=M\n"              # D = *SP (value to pop)
            "@R13\n"
            "A=M\n"              # A = target address
            "M=D\n"              # RAM[LCL + index] = value
        )


    # push this, that, argument, local
    def write_pust_base(self, segment_base: str, index: int) -> None: 
           
        """Writes assembly code for 'push segment_base index'."""
        self.output_stream.write(
            f"// push {segment_base} {index}\n"
            f"@{segment_base}\n"
            "D=M\n"              # D = base address of segment
            f"@{index}\n"
            "A=D+A\n"            # A = segment_base + index
            "D=M\n"              # D = RAM[segment_base + index]
            "@SP\n"
            "A=M\n"              # A = SP (first free stack slot)
            "M=D\n"              # *SP = value
            "@SP\n"
            "M=M+1\n"            # SP++
        )
    # pop this, that, argument, local    
    def write_pop_base(self, segment_base: str, index: int) -> None:
        """Writes assembly code for 'pop segment_base index'."""
        self.output_stream.write(
            f"// pop {segment_base} {index}\n"
            f"@{segment_base}\n"
            "D=M\n"              # D = base address of segment
            f"@{index}\n"
            "D=D+A\n"            # D = segment_base + index
            "@R13\n"
            "M=D\n"              # R13 = target address
            "@SP\n"
            "AM=M-1\n"           # SP--; A = SP
            "D=M\n"              # D = *SP (value to pop)
            "@R13\n"
            "A=M\n"              # A = target address
            "M=D\n"              # RAM[segment_base + index] = value
        )
    # 
    # calcul the address of temp+index = 5+index, store it in R13, then pop the stack value into D,write D into RAM[R13]
    def write_pop_temp(self, index: int) -> None:
        """Writes assembly code for 'pop temp index'."""
        self.output_stream.write(
            f"// pop temp {index}\n"
            "@5\n"
            "D=A\n"              # D = 5 (base address of temp segment)
            f"@{index}\n"
            "D=D+A\n"            # D = 5 + index
            "@R13\n"
            "M=D\n"              # R13 = target address (5 + index)

            "@SP\n"
            "AM=M-1\n"           # SP-- ; A=SP ; M=*SP (top stack value)
            "D=M\n"              # D = popped value

            "@R13\n"
            "A=M\n"              # A = target address
            "M=D\n"              # RAM[5 + index] = D
        )

# push temp+index = 5+index, read RAM[5+index] into D, push D onto stack
    def write_push_temp(self, index: int) -> None:
        """Writes assembly code for 'push temp index'."""
        self.output_stream.write(
            f"// push temp {index}\n"
            "@5\n"
            "D=A\n"              # D = 5 (base address of temp segment)
            f"@{index}\n"
            "A=D+A\n"            # A = 5 + index
            "D=M\n"              # D = RAM[5 + index]

            "@SP\n"
            "A=M\n"              # A = SP (first free stack slot)
            "M=D\n"              # *SP = D

            "@SP\n"
            "M=M+1\n"            # SP++
        )   

    def write_push_pointer(self, index: int) -> None:
        """Writes assembly code for 'push pointer index'."""
        base_map = {
            0: "THIS",
            1: "THAT"
        }
        segment_base = base_map[index]
        self.output_stream.write(
            f"// push pointer {index}\n"
            f"@{segment_base}\n"
            "D=M\n"              # D = RAM[segment_base]

            "@SP\n"
            "A=M\n"              # A = SP (first free stack slot)
            "M=D\n"              # *SP = D

            "@SP\n"
            "M=M+1\n"            # SP++
        )   
    def write_pop_pointer(self, index: int) -> None:
        """Writes assembly code for 'pop pointer index'."""
        base_map = {
            0: "THIS",
            1: "THAT"
        }
        segment_base = base_map[index]
        self.output_stream.write(
            f"// pop pointer {index}\n"
            "@SP\n"
            "AM=M-1\n"           # SP--; A = SP
            "D=M\n"              # D = *SP (value to pop)

            f"@{segment_base}\n"
            "M=D\n"              # RAM[segment_base] = D
        )            

       
    
                    
                



        

    def write_label(self, label: str) -> None:
        """Writes assembly code that affects the label command. 
        Let "Xxx.foo" be a function within the file Xxx.vm. The handling of
        each "label bar" command within "Xxx.foo" generates and injects the symbol
        "Xxx.foo$bar" into the assembly code stream.
        When translating "goto bar" and "if-goto bar" commands within "foo",
        the label "Xxx.foo$bar" must be used instead of "bar".

        Args:
            label (str): the label to write.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        pass
    
    def write_goto(self, label: str) -> None:
        """Writes assembly code that affects the goto command.

        Args:
            label (str): the label to go to.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        pass
    
    def write_if(self, label: str) -> None:
        """Writes assembly code that affects the if-goto command. 

        Args:
            label (str): the label to go to.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        pass
    
    def write_function(self, function_name: str, n_vars: int) -> None:
        """Writes assembly code that affects the function command. 
        The handling of each "function Xxx.foo" command within the file Xxx.vm
        generates and injects a symbol "Xxx.foo" into the assembly code stream,
        that labels the entry-point to the function's code.
        In the subsequent assembly process, the assembler translates this 
        symbol into the physical address where the function code starts.

        Args:
            function_name (str): the name of the function.
            n_vars (int): the number of local variables of the function.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        # The pseudo-code of "function function_name n_vars" is:
        # (function_name)       // injects a function entry label into the code
        # repeat n_vars times:  // n_vars = number of local variables
        #   push constant 0     // initializes the local variables to 0
        pass
    
    def write_call(self, function_name: str, n_args: int) -> None:
        """Writes assembly code that affects the call command. 
        Let "Xxx.foo" be a function within the file Xxx.vm.
        The handling of each "call" command within Xxx.foo's code generates and
        injects a symbol "Xxx.foo$ret.i" into the assembly code stream, where
        "i" is a running integer (one such symbol is generated for each "call"
        command within "Xxx.foo").
        This symbol is used to mark the return address within the caller's 
        code. In the subsequent assembly process, the assembler translates this
        symbol into the physical memory address of the command immediately
        following the "call" command.

        Args:
            function_name (str): the name of the function to call.
            n_args (int): the number of arguments of the function.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        # The pseudo-code of "call function_name n_args" is:
        # push return_address   // generates a label and pushes it to the stack
        # push LCL              // saves LCL of the caller
        # push ARG              // saves ARG of the caller
        # push THIS             // saves THIS of the caller
        # push THAT             // saves THAT of the caller
        # ARG = SP-5-n_args     // repositions ARG
        # LCL = SP              // repositions LCL
        # goto function_name    // transfers control to the callee
        # (return_address)      // injects the return address label into the code
        pass
    
    def write_return(self) -> None:
        """Writes assembly code that affects the return command."""
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        # The pseudo-code of "return" is:
        # frame = LCL                   // frame is a temporary variable
        # return_address = *(frame-5)   // puts the return address in a temp var
        # *ARG = pop()                  // repositions the return value for the caller
        # SP = ARG + 1                  // repositions SP for the caller
        # THAT = *(frame-1)             // restores THAT for the caller
        # THIS = *(frame-2)             // restores THIS for the caller
        # ARG = *(frame-3)              // restores ARG for the caller
        # LCL = *(frame-4)              // restores LCL for the caller
        # goto return_address           // go to the return address
        pass
