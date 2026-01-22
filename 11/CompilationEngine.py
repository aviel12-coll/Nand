"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
from JackTokenizer import JackTokenizer
from VMWriter import VMWriter
from SymbolTable import SymbolTable
import typing


class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """

    CLASS_VAR_DEC_KEYWORDS= ("STATIC", "FIELD")
    SUBROUTINE_KEYWORDS = ("CONSTRUCTOR", "FUNCTION", "METHOD")
    WORD_STATEMENTS = ("LET", "IF", "WHILE", "DO", "RETURN")
    OPERATORS = {"+", "-", "*", "/", "&", "|", "<", ">", "="}
    CONST_TYPE = {"INT_CONST", "STRING_CONST"}
    KEYWORD_CONSTANTS = ("TRUE", "FALSE", "NULL", "THIS")


    def __init__(self, input_stream: "JackTokenizer", output_stream) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        # Your code goes here!
        # Note that you can write to output_stream like so:
        # output_stream.write("Hello world! \n")
        self.input_file= input_stream
        self.SymbolTable= SymbolTable()
        self.VMWriter= VMWriter(output_stream)
        self.while_counter = 0
        self.if_counter = 0

    def kind_to_segment(self, kind: str) -> str:
        """Converts SymbolTable kind to VM segment name."""
        mapping = {
            "STATIC": "STATIC",
            "FIELD": "THIS",
            "ARG": "ARG",
            "VAR": "LOCAL"
        }
        return mapping.get(kind, kind)

    def compile_class(self) -> None:
        """Compiles a complete class."""
        # Your code goes here!
        #write <class> to output file
           # Write opening tokens tag
        # advance to first token and verify it's 'class'
        self.input_file.advance()
        self.verify_token("class")
        # advance to class name
        self.input_file.advance()
        self.class_name = self.input_file.identifier()
        # advance to '{'
        self.input_file.advance()
        self.verify_token("{")
        # body of the function
        self.input_file.advance()
        while (self.input_file.token_type() == "KEYWORD" and self.input_file.keyword()
                in CompilationEngine.CLASS_VAR_DEC_KEYWORDS):
            self.compile_class_var_dec()

        while (self.input_file.token_type() == "KEYWORD" and
        self.input_file.keyword() in CompilationEngine.SUBROUTINE_KEYWORDS):
            self.compile_subroutine()    
        
        # close the class with '}'
        self.verify_token("}")
  
         



    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        # Your code goes here!
        # 'static' or 'field'
        kind = self.input_file.keyword()  # "STATIC" or "FIELD"
        # advance to type
        self.input_file.advance()
        var_type = self.input_file.keyword().lower() if self.input_file.token_type() == "KEYWORD" else self.input_file.identifier()
        # advance to varName
        self.input_file.advance()
        var_name = self.input_file.identifier()
        self.SymbolTable.define(var_name, var_type, kind)
        # advance to (',' or ';')
        self.input_file.advance()
        while self.input_file.symbol() == ',':
            self.verify_token(",")
            # advance to varName
            self.input_file.advance()
            var_name = self.input_file.identifier()
            self.SymbolTable.define(var_name, var_type, kind)
            # advance to (',' or ';')
            self.input_file.advance()
        # now the symbol is ';'
        self.verify_token(";")
        # advance to next token
        self.input_file.advance()
        

    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """
        # Your code goes here!
        subroutine_type = self.input_file.keyword()
        # 'constructor' | 'function' | 'method'
         # reset the symbol table for the new subroutine
        self.SymbolTable.start_subroutine()
        # advance to return type
        self.input_file.advance()

        # return type
        self.input_file.advance()
        subroutine_name = self.input_file.identifier() 
        # subroutine name
        self.input_file.advance()
        # store subroutine name for VM function declaration
        full_name = f"{self.class_name}.{subroutine_name}"

          # if method: add implicit 'this'
        if subroutine_type == "METHOD":
            self.SymbolTable.define("this", self.class_name, "ARG")

        # '('
        self.verify_token("(")
        self.input_file.advance()

        # parameter list
        self.compile_parameter_list()
        # ')'
        self.verify_token(")")
        self.input_file.advance()
        # subroutine body
        self.verify_token("{")
        self.input_file.advance()
        while (self.input_file.token_type() == "KEYWORD" and
                self.input_file.keyword() == "VAR"):
                self.compile_var_dec()
        n_locals = self.SymbolTable.var_count("VAR")
        self.VMWriter.write_function(full_name, n_locals)
        self.handle_subroutine_setup(subroutine_type)
         
    # statements       
        self.compile_statements()
        self.verify_token("}")
        self.input_file.advance()

    def handle_subroutine_setup(self, subroutine_type):
        if subroutine_type == "METHOD":
            self.VMWriter.write_push("ARG", 0)
            self.VMWriter.write_pop("POINTER", 0)

        elif subroutine_type == "CONSTRUCTOR":
            num_fields = self.SymbolTable.var_count("FIELD")
            self.VMWriter.write_push("CONST", num_fields)
            self.VMWriter.write_call("Memory.alloc", 1)
            self.VMWriter.write_pop("POINTER", 0)

    # function -> intentionally no code    

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".
        """
        # Your code goes here!
        #  if the list is nit empty
        if self.input_file.token_type() == "SYMBOL" and self.input_file.symbol() == ")":
            return
         # first parameter
        if self.input_file.token_type() == "KEYWORD":
            var_type = self.input_file.keyword()
        else:
            var_type = self.input_file.identifier()
        self.input_file.advance()

        var_name = self.input_file.identifier()
        self.SymbolTable.define(var_name, var_type, "ARG")
        self.input_file.advance()

        while (self.input_file.token_type() == "SYMBOL" and self.input_file.symbol() == ","):
            self.input_file.advance()
            # type
            if self.input_file.token_type() == "KEYWORD":
                var_type = self.input_file.keyword()
            else:
                var_type = self.input_file.identifier()
            self.input_file.advance()
            # varName
            var_name = self.input_file.identifier()
            self.SymbolTable.define(var_name, var_type, "ARG")
            self.input_file.advance() 




        if self.input_file.symbol() != ")":
            # type
            self.input_file.advance()
            # varName
            self.input_file.advance()
            while self.input_file.symbol() == ",":
                # ','
                self.verify_token(",")
                self.input_file.advance()
                # type
                self.input_file.advance()
                # varName
                self.input_file.advance()
            
        

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        # Your code goes here!
        # 'var' keyword - advance to type
        self.input_file.advance()
        # type keyword
        var_type = self.input_file.keyword().lower() if self.input_file.token_type() == "KEYWORD" else self.input_file.identifier()
        self.input_file.advance()
        # varName
        var_name = self.input_file.identifier()
        self.SymbolTable.define(var_name, var_type, "VAR")
        self.input_file.advance()
        while self.input_file.symbol() == ",":
            # ',' 
            self.verify_token(",")
            self.input_file.advance()
            # varName
            var_name = self.input_file.identifier()
            self.SymbolTable.define(var_name, var_type, "VAR")
            self.input_file.advance()
        # ';'
        self.verify_token(";")
        self.input_file.advance()


    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".
        """
        # Your code goes here!
        while (self.input_file.token_type() == "KEYWORD" and
               self.input_file.keyword() in self.WORD_STATEMENTS):  
            if self.input_file.keyword() == "LET":
                self.compile_let()
            elif self.input_file.keyword() == "IF":
                self.compile_if()
            elif self.input_file.keyword() == "WHILE":
                self.compile_while()
            elif self.input_file.keyword() == "DO":
                self.compile_do()
            elif self.input_file.keyword() == "RETURN":
                self.compile_return()   

    def compile_do(self) -> None:
        """Compiles a do statement."""
        # Your code goes here!
        # 'do' keyword - already on 'do', advance to first identifier
        self.input_file.advance()

        # first identifier: subroutine name or className|varName
        name= self.input_file.identifier()
        n_Args=0

        # advance to see if next is '.' or '('
        self.input_file.advance()

        # first case: className.subroutineName() or varName.subroutineName()
        if self.input_file.token_type() == "SYMBOL" and self.input_file.symbol() == ".":
            if self.SymbolTable.kind_of(name) is not None:
                # method call on an object: push the object as the first argument
                var_kind= self.SymbolTable.kind_of(name)
                var_index= self.SymbolTable.index_of(name)
                obj_type= self.SymbolTable.type_of(name)
                self.VMWriter.write_push(self.kind_to_segment(var_kind), var_index)
                n_Args += 1
                class_name= obj_type

            else:
                # class function call 
                class_name= name
            # '.' already verified, advance to subroutine name
            self.input_file.advance()
            subroutine_name= self.input_file.identifier()
            # advance past subroutine name
            self.input_file.advance()

        # subroutineName() - method call on 'this'
        else:
            # method call on 'this': push 'this' as the first argument
            self.VMWriter.write_push("POINTER", 0)
            n_Args += 1
            class_name= self.class_name
            subroutine_name= name
        # '('
        self.verify_token("(")      
        self.input_file.advance()
        n_Args += self.compile_expression_list()

        # ')'
        self.verify_token(")")
        self.input_file.advance()

        full_name= f"{class_name}.{subroutine_name}"
        self.VMWriter.write_call(full_name, n_Args)
        self.VMWriter.write_pop("TEMP", 0)

        # ";"
        self.verify_token(";")
        self.input_file.advance()




    def compile_let(self) -> None:
        """Compiles a let statement."""
        # Your code goes here!
        # 'let' keyword - advance to varName
        self.input_file.advance()
        var_name= self.input_file.identifier()

        var_kind= self.SymbolTable.kind_of(var_name)
        if var_kind is None:
            raise ValueError(f"Variable '{var_name}' not found in symbol table (let statement)")
        var_index= self.SymbolTable.index_of(var_name)  
        segement= self.kind_to_segment(var_kind)
        is_array= False
        
        # advance past varName
        self.input_file.advance()
        
        # if there is an array access
        if self.input_file.token_type() == "SYMBOL" and self.input_file.symbol() == "[":
            is_array = True
            self.VMWriter.write_push(segement, var_index)

            # '['
            self.input_file.advance()
            # expression
            self.compile_expression()
            # ']'
            self.verify_token("]")
            self.input_file.advance()

            self.VMWriter.write_arithmetic("ADD")
        # '='
        self.verify_token("=")
        self.input_file.advance()   
        # expression
        self.compile_expression()
        if is_array:
            # for array assignment
            self.VMWriter.write_pop("TEMP", 0)
            self.VMWriter.write_pop("POINTER", 1)
            self.VMWriter.write_push("TEMP", 0)
            self.VMWriter.write_pop("THAT", 0)
        else:
            self.VMWriter.write_pop(segement, var_index)

        # ';'
        self.verify_token(";")
        self.input_file.advance()
            

    def compile_while(self) -> None:
        """Compiles a while statement."""
        # Your code goes here!
        # 'while' keyword
        num = self.while_counter
        self.while_counter += 1
        start_label = f"WHILE_EXP{num}"
        end_label = f"WHILE_END{num}"
        
        self.verify_token("while")
        self.input_file.advance() # '('
        self.verify_token("(")
        self.input_file.advance()   # expression
        self.VMWriter.write_label(start_label)
        
        # expression
        self.compile_expression()   
        
        # ')'
        self.verify_token(")")
        self.input_file.advance()   # '{'

         # if condition is false -> exit loop
        self.VMWriter.write_arithmetic("NOT")
        self.VMWriter.write_if(end_label)
       
        self.verify_token("{")
        self.input_file.advance()   # statements
        self.compile_statements()
        # '}'
        self.verify_token("}")
        self.input_file.advance()

        # go back to beginning of while
        self.VMWriter.write_goto(start_label)
        self.VMWriter.write_label(end_label)
        

    def compile_return(self) -> None:
        """Compiles a return statement."""
        # Your code goes here!
        # 'return' keyword
        self.input_file.advance()
        # if there is an expression
        if not (self.input_file.token_type() == "SYMBOL" and self.input_file.symbol() == ";"):
            self.compile_expression()
        else:
            # void function: push 0 as return value
            self.VMWriter.write_push("CONST", 0)
        # ';'
        self.verify_token(";")
        self.VMWriter.write_return()
        self.input_file.advance()

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        # Your code goes here!
        # 'if' keyword
        num = self.if_counter
        self.if_counter += 1
        else_label = f"IF_ELSE{num}"
        end_label = f"IF_END{num}"
        
        self.verify_token("if")
        self.input_file.advance()
        # '('
        self.verify_token("(")
        self.input_file.advance()
        # expression
        self.compile_expression()
        # ')'
        self.verify_token(")")
        self.input_file.advance()

        # '{'
        self.verify_token("{")
        self.input_file.advance()
        
        self.VMWriter.write_arithmetic("NOT")
        self.VMWriter.write_if(else_label)
        
        # statements
        self.compile_statements()
        # '}'
        self.verify_token("}")
        self.input_file.advance()
        
        # go to end (skip else)
        self.VMWriter.write_goto(end_label)
        
        # else label
        self.VMWriter.write_label(else_label)
        
        # if there is an 'else' clause
        if self.input_file.token_type() == "KEYWORD" and self.input_file.keyword() == "ELSE":
            # 'else' keyword
            self.verify_token("else")
            self.input_file.advance()
            # '{'
            self.verify_token("{")
   
            self.input_file.advance()
            # statements
            self.compile_statements()
            # '}'
            self.verify_token("}")
 
            self.input_file.advance()
        
        # end label
        self.VMWriter.write_label(end_label)      



    def compile_expression(self) -> None:
        """Compiles an expression."""
        # Your code goes here!

        # term
        self.compile_term()
        # while the current token is an operator
        while (self.input_file.token_type() == "SYMBOL" and
                self.input_file.symbol() in CompilationEngine.OPERATORS):
                # operator
   
                operator = self.input_file.symbol()
                self.input_file.advance()
                self.compile_term()   # next term
                # write VM code for operator

                if operator == "+":
                    self.VMWriter.write_arithmetic("ADD")
                elif operator == "-":
                    self.VMWriter.write_arithmetic("SUB")   
                elif operator == "*":   
                    self.VMWriter.write_call("Math.multiply", 2)
                elif operator == "/":
                    self.VMWriter.write_call("Math.divide", 2)
                elif operator == "&":
                    self.VMWriter.write_arithmetic("AND")
                elif operator == "|":   
                    self.VMWriter.write_arithmetic("OR")
                elif operator == "<":
                    self.VMWriter.write_arithmetic("LT")
                elif operator == ">":
                    self.VMWriter.write_arithmetic("GT")
                elif operator == "=":
                    self.VMWriter.write_arithmetic("EQ")


    def compile_constant(self, token_type: str) -> None:
        """Compiles an integer or string constant."""

        # integer constant
        if token_type == "INT_CONST":
            value = self.input_file.int_val()
            self.VMWriter.write_push("CONST", value)
            self.input_file.advance()

        # string constant
        elif token_type == "STRING_CONST":
            string = self.input_file.string_val()

            # allocate new string
            self.VMWriter.write_push("CONST", len(string))
            self.VMWriter.write_call("String.new", 1)

            # append characters
            for ch in string:
                self.VMWriter.write_push("CONST", ord(ch))
                self.VMWriter.write_call("String.appendChar", 2)

            self.input_file.advance()

        else:
            raise ValueError("compile_constant called on non-constant token")  

    def Keyboard_constant(self, token_type:str) -> None: 
        """Compiles a keyword constant."""  
        keyword = self.input_file.keyword()
        if keyword == "TRUE":
            self.VMWriter.write_push("CONST", 0)
            self.VMWriter.write_arithmetic("NOT")
        elif keyword in {"FALSE", "NULL"}:
            self.VMWriter.write_push("CONST", 0)
        elif keyword == "THIS":
            self.VMWriter.write_push("POINTER", 0)
        self.input_file.advance()             




    def compile_term(self) -> None:
        """Compiles a term. 
        This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routing must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of "[", "(", or "." suffices
        to distinguish between the three possibilities. Any other token is not
        part of this term and should not be advanced over.
        """
        # Your code goes here!
        token_type = self.input_file.token_type()

            # integer constant or string constant
        if token_type  in CompilationEngine.CONST_TYPE:
            self.compile_constant(token_type)


         # keyword constant true, false, null, this   
        elif token_type == "KEYWORD" and self.input_file.keyword() in CompilationEngine.KEYWORD_CONSTANTS:
            self.Keyboard_constant(token_type)
           

        # '(' expression ')'    
        elif token_type == "SYMBOL" and self.input_file.symbol() == "(":
            self.input_file.advance()
            self.compile_expression()
            self.input_file.advance()

        # unaryOp term
        elif token_type == "SYMBOL" and self.input_file.symbol() in ("-", "~"):
            operator = self.input_file.symbol()
            self.input_file.advance()
            self.compile_term()
            if operator == "-":
                self.VMWriter.write_arithmetic("NEG")
            elif operator == "~":
                self.VMWriter.write_arithmetic("NOT")    
        # varName | varName '[' expression ']' | subroutineCall
        elif token_type == "IDENTIFIER":
            # varName
            name = self.input_file.identifier()
            self.input_file.advance()



            # if there is an array access
            if self.input_file.token_type() == "SYMBOL" and self.input_file.symbol() == "[":
                kind= self.SymbolTable.kind_of(name)
                index= self.SymbolTable.index_of(name)
                segement= self.kind_to_segment(kind)
                self.VMWriter.write_push(segement, index)
                self.input_file.advance()
                self.compile_expression()
                self.verify_token("]")
                self.input_file.advance()
                self.VMWriter.write_arithmetic("ADD")
                self.VMWriter.write_pop("POINTER", 1)
                self.VMWriter.write_push("THAT", 0)

            # if there is a subroutine call
            elif self.input_file.token_type() == "SYMBOL" and self.input_file.symbol() in (".", "("):
                n_Args=0
                # if it's className.methodName or varName.methodName
                if self.input_file.symbol() == ".":
                    if self.SymbolTable.kind_of(name) is not None:
                        kind = self.SymbolTable.kind_of(name)
                        index = self.SymbolTable.index_of(name)
                        segment = self.kind_to_segment(kind)
                        self.VMWriter.write_push(segment, index)
                        n_Args += 1
                        class_name = self.SymbolTable.type_of(name)
                    else:
                        class_name = name
                    # advance past '.'
                    self.input_file.advance()
                    # subroutine name
                    subroutine = self.input_file.identifier()
                    self.input_file.advance()
                    # '('
                    self.verify_token("(")
                    self.input_file.advance()
                else:
                    # direct call like foo()
                    class_name = self.class_name
                    subroutine = name
                    self.VMWriter.write_push("POINTER", 0)
                    n_Args += 1
                    # advance past '('
                    self.input_file.advance()
                # expression list
                n_Args += self.compile_expression_list()
                self.verify_token(")")
                self.input_file.advance()
                full_name = f"{class_name}.{subroutine}"    
                self.VMWriter.write_call(full_name, n_Args)
            # simple varName
            else:
                kind= self.SymbolTable.kind_of(name)
                if kind is None:
                    raise ValueError(f"Variable '{name}' not found in symbol table")
                index= self.SymbolTable.index_of(name)
                segement= self.kind_to_segment(kind)
                self.VMWriter.write_push(segement, index)

   




    def compile_expression_list(self) -> int:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        # Your code goes here!
        # empty list: next token is ')'
        count=0
        if self.input_file.token_type() == "SYMBOL" and self.input_file.symbol() == ")":
            return count
        

        # first expression
        self.compile_expression()
        count +=1   

        # (, expression)*
        while self.input_file.token_type() == "SYMBOL" and self.input_file.symbol() == ",":
              # ','
            self.input_file.advance()
            self.compile_expression()
            count +=1
        return count

      
    def verify_token(self, expected: str) -> None:
        """Verifies that the current token matches the expected string.
        
        Args:
            expected (str): The expected token value.
            
        Raises:
            ValueError: If the current token doesn't match the expected string.
        """
        token_type = self.input_file.token_type()
        if token_type == "KEYWORD":
            cur_token = self.input_file.keyword().lower()
        elif token_type == "SYMBOL":
            cur_token = self.input_file.symbol()
        elif token_type == "IDENTIFIER":
            cur_token = self.input_file.identifier()
        elif token_type == "INT_CONST":
            cur_token = str(self.input_file.int_val())
        elif token_type == "STRING_CONST":
            cur_token = self.input_file.string_val()
        else:
            cur_token = "UNKNOWN"
            
        if cur_token != expected:
            raise ValueError(f"Expected '{expected}', got '{cur_token}'")


