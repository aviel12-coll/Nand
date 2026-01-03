"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
from JackTokenizer import JackTokenizer


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
        self.input_file=input_stream
        self.output_file=output_stream 

    def compile_class(self) -> None:
        """Compiles a complete class."""
        # Your code goes here!
        #write <class> to output file
           # Write opening tokens tag
        self.opening_tag("class")
        # advance to first token and verify it's 'class'
        self.input_file.advance()
        self.verify_token("class")
        self.write_line()
        # advance to class name
        self.input_file.advance()
        self.write_line()
        # advance to '{'
        self.input_file.advance()
        self.verify_token("{")
        self.write_line()
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
        self.write_line()
        self.output_file.write("</class>\n")    
  
         



    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        # Your code goes here!
        self.opening_tag("classVarDec")
        # 'static' or 'field'
        self.write_line()
        # advance to type
        self.input_file.advance()
        self.write_line()
        # advance to varName
        self.input_file.advance()
        self.write_line()
        # advance to (',' or ';')
        self.input_file.advance()
        while self.input_file.symbol() == ',':
            self.verify_token(",")
            self.write_line()
            # advance to varName
            self.input_file.advance()
            self.write_line()
            # advance to (',' or ';')
            self.input_file.advance()
        # now the symbol is ';'
        self.verify_token(";")
        self.write_line()
        self.output_file.write(f"</classVarDec>\n")
        # advance to next token
        self.input_file.advance()
        

    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """
        # Your code goes here!
        self.opening_tag("subroutineDec")
        self.write_line()
        self.input_file.advance()

        # return type
        self.write_line()
        self.input_file.advance()
        # subroutine name
        self.write_line()
        self.input_file.advance()
        # '('
        self.verify_token("(")
        self.write_line()
        self.input_file.advance()
        # parameter list
        self.compile_parameter_list()
        # ')'
        self.verify_token(")")
        self.write_line()
        self.input_file.advance()
        # subroutine body
        self.opening_tag("subroutineBody")
        self.verify_token("{")
        self.write_line()
        self.input_file.advance()
        while (self.input_file.token_type() == "KEYWORD" and
                self.input_file.keyword() == "VAR"):
                self.compile_var_dec()
        self.compile_statements()
        self.verify_token("}")
        self.write_line()
        self.output_file.write(f"</subroutineBody>\n")
        self.output_file.write(f"</subroutineDec>\n")
        self.input_file.advance()

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".
        """
        # Your code goes here!
        self.opening_tag("parameterList")
        #  if the list is nit empty
        if self.input_file.symbol() != ")":
            # type
            self.write_line()
            self.input_file.advance()
            # varName
            self.write_line()
            self.input_file.advance()
            while self.input_file.symbol() == ",":
                # ','
                self.verify_token(",")
                self.write_line()
                self.input_file.advance()
                # type
                self.write_line()
                self.input_file.advance()
                # varName
                self.write_line()
                self.input_file.advance()
        self.output_file.write(f"</parameterList>\n")        
            
        

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        # Your code goes here!
        self.opening_tag("varDec")
        # 'var' keyword
        self.write_line()   
        self.input_file.advance()
        # type keyword
        self.write_line()
        self.input_file.advance()
        # varName
        self.write_line()
        self.input_file.advance()
        while self.input_file.symbol() == ",":
            # ',' 
            self.verify_token(",")
            self.write_line()
            self.input_file.advance()
            # varName
            self.write_line()
            self.input_file.advance()
        # ';'
        self.verify_token(";")
        self.write_line()
        self.input_file.advance()

        self.output_file.write(f"</varDec>\n")

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".
        """
        # Your code goes here!
        self.opening_tag("statements")
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
        self.output_file.write(f"</statements>\n")                

    def compile_do(self) -> None:
        """Compiles a do statement."""
        # Your code goes here!
        self.opening_tag("doStatement")
        # 'do' keyword
        self.write_line()
        self.input_file.advance()
        # subroutine call
        self.write_line()
        self.input_file.advance()



        # if there is a '.' like in ClassName.subroutineName or varName.subroutineName
        if self.input_file.symbol() == ".":
            self.write_line()
            self.input_file.advance()
            # subroutine name
            self.write_line()
            self.input_file.advance()
        # '('
        self.verify_token("(")
        self.write_line()   
        self.input_file.advance()
        # expression list
        self.compile_expression_list()

        # ')'
        self.verify_token(")")
        self.write_line()
        self.input_file.advance()

        # ';'
        self.verify_token(";")
        self.write_line()
        self.input_file.advance()
        self.output_file.write(f"</doStatement>\n")




    def compile_let(self) -> None:
        """Compiles a let statement."""
        # Your code goes here!
        self.opening_tag("letStatement")
        # 'let' keyword
        self.write_line()
        self.input_file.advance()
        # varName
        self.write_line()
        self.input_file.advance()
        # if there is an array access
        if self.input_file.symbol() == "[":
            # '['
            self.write_line()
            self.input_file.advance()
            # expression
            self.compile_expression()
            # ']'
            self.verify_token("]")
            self.write_line()
            self.input_file.advance()
        # '='
        self.verify_token("=")
        self.write_line()    
        self.input_file.advance()   
        # expression
        self.compile_expression()
        # ';'
        self.verify_token(";")  
        self.write_line()
        self.input_file.advance()
        self.output_file.write(f"</letStatement>\n")
            

    def compile_while(self) -> None:
        """Compiles a while statement."""
        # Your code goes here!
        self.opening_tag("whileStatement")
        # 'while' keyword
        self.write_line()
        self.input_file.advance()
        # '('
        self.verify_token("(")
        self.write_line()
        self.input_file.advance()   
        # expression
        self.compile_expression()   
        # ')'
        self.verify_token(")")
        self.write_line()
        self.input_file.advance()
        # '{'
        self.verify_token("{")
        self.write_line()
        self.input_file.advance()
        # statements
        self.compile_statements()
        # '}'
        self.verify_token("}")
        self.write_line()
        self.input_file.advance()
        self.output_file.write(f"</whileStatement>\n")
        

    def compile_return(self) -> None:
        """Compiles a return statement."""
        # Your code goes here!
        self.opening_tag("returnStatement")
        # 'return' keyword
        self.write_line()
        self.input_file.advance()
        # if there is an expression
        if self.input_file.symbol() != ";":
            self.compile_expression()
        # ';'
        self.verify_token(";")
        self.write_line()
        self.input_file.advance()
        self.output_file.write(f"</returnStatement>\n")

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        # Your code goes here!
        self.opening_tag("ifStatement")
        # 'if' keyword
        self.write_line()
        self.input_file.advance()
        # '('
        self.verify_token("(")
        self.write_line()
        self.input_file.advance()
        # expression
        self.compile_expression()
        # ')'
        self.verify_token(")")
        self.write_line()
        self.input_file.advance()

        # '{'
        self.verify_token("{")
        self.write_line()
        self.input_file.advance()
        # statements
        self.compile_statements()
        # '}'
        self.verify_token("}")
        self.write_line()
        self.input_file.advance()
        # if there is an 'else' clause
        if self.input_file.token_type() == "KEYWORD" and self.input_file.keyword() == "ELSE":
            # 'else' keyword
            self.write_line()
            self.input_file.advance()
            # '{'
            self.verify_token("{")
            self.write_line()
            self.input_file.advance()
            # statements
            self.compile_statements()
            # '}'
            self.verify_token("}")
            self.write_line()
            self.input_file.advance()   
        self.output_file.write(f"</ifStatement>\n")


    def compile_expression(self) -> None:
        """Compiles an expression."""
        # Your code goes here!
        self.opening_tag("expression")
        # term
        self.compile_term()
        # while the current token is an operator
        while (self.input_file.token_type() == "SYMBOL" and
                self.input_file.symbol() in CompilationEngine.OPERATORS):
                # operator
                self.write_line()
                self.input_file.advance()
                # term
                self.compile_term()
        self.output_file.write(f"</expression>\n")

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
        self.opening_tag("term")
        token_type = self.input_file.token_type()

            # integer constant or string constant
        if token_type  in CompilationEngine.CONST_TYPE:
            self.write_line()
            self.input_file.advance()


         # keyword constant true, false, null, this   
        elif token_type == "KEYWORD" and self.input_file.keyword() in CompilationEngine.KEYWORD_CONSTANTS:
            self.write_line()
            self.input_file.advance()  

        # '(' expression ')'    
        elif token_type == "SYMBOL" and self.input_file.symbol() == "(":
            self.verify_token("(")
            self.write_line()
            self.input_file.advance()
            self.compile_expression()
            self.verify_token(")")
            self.write_line()
            self.input_file.advance()
        # unaryOp term
        elif token_type == "SYMBOL" and self.input_file.symbol() in ("-", "~"):
            self.write_line()
            self.input_file.advance()
            self.compile_term()
        # varName | varName '[' expression ']' | subroutineCall
        elif token_type == "IDENTIFIER":
            # varName
            self.write_line()
            self.input_file.advance()
            # if there is an array access
            if self.input_file.token_type() == "SYMBOL" and self.input_file.symbol() == "[":
                # '['
                self.verify_token("[")
                self.write_line()
                self.input_file.advance()
                # expression
                self.compile_expression()
                # ']'
                self.verify_token("]")
                self.write_line()
                self.input_file.advance()
            # if there is a subroutine call
            elif self.input_file.token_type() == "SYMBOL" and self.input_file.symbol() in (".", "("):
                # if it's className.methodName or varName.methodName
                if self.input_file.symbol() == ".":
                    self.verify_token(".")
                    self.write_line()
                    self.input_file.advance()
                    # method name
                    self.write_line()
                    self.input_file.advance()
                # '('
                self.verify_token("(")
                self.write_line()
                self.input_file.advance()
                # expression list
                self.compile_expression_list()
                # ')'
                self.verify_token(")")
                self.write_line()
                self.input_file.advance()  
        self.output_file.write(f"</term>\n")    




    def compile_expression_list(self) -> None:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        # Your code goes here!
        self.opening_tag("expressionList")
        # empty list: next token is ')'
        if self.input_file.token_type() == "SYMBOL" and self.input_file.symbol() == ")":
            self.output_file.write("</expressionList>\n")
            return

        # first expression
        self.compile_expression()

        # (, expression)*
        while self.input_file.token_type() == "SYMBOL" and self.input_file.symbol() == ",":
            self.write_line()      # ','
            self.input_file.advance()
            self.compile_expression()

        self.output_file.write("</expressionList>\n")
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

    def opening_tag(self, tag: str) -> None:
        """Writes an opening XML tag in the output file.

        Args:
            tag (str): the tag name.
        """
        # Your code goes here!
        self.output_file.write(f"<{tag}>\n")

    def write_line(self) -> None:
        """Writes current token with appropriate XML tags to the output file."""
        token_type = self.input_file.token_type()
        if token_type == "KEYWORD":
            # Write keyword in lowercase for XML output
            keyword = self.input_file.keyword().lower()
            self.output_file.write(f"<keyword> {keyword} </keyword>\n")
        elif token_type == "SYMBOL":
            self.output_file.write(f"<symbol> {self.input_file.symbol()} </symbol>\n")
        elif token_type == "IDENTIFIER":
            self.output_file.write(f"<identifier> {self.input_file.identifier()} </identifier>\n")
        elif token_type == "INT_CONST":
            self.output_file.write(f"<integerConstant> {self.input_file.int_val()} </integerConstant>\n")
        elif token_type == "STRING_CONST":
            self.output_file.write(f"<stringConstant> {self.input_file.string_val()} </stringConstant>\n") 