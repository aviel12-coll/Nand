"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
from pydoc import text
import typing


class JackTokenizer:
    """Removes all comments from the input stream and breaks it
    into Jack language tokens, as specified by the Jack grammar.
    
    # Jack Language Grammar

    A Jack file is a stream of characters. If the file represents a
    valid program, it can be tokenized into a stream of valid tokens. The
    tokens may be separated by an arbitrary number of whitespace characters, 
    and comments, which are ignored. There are three possible comment formats: 
    /* comment until closing */ , /** API comment until closing */ , and 
    // comment until the line's end.

    - 'xxx': quotes are used for tokens that appear verbatim ('terminals').
    - xxx: regular typeface is used for names of language constructs 
           ('non-terminals').
    - (): parentheses are used for grouping of language constructs.
    - x | y: indicates that either x or y can appear.
    - x?: indicates that x appears 0 or 1 times.
    - x*: indicates that x appears 0 or more times.

    ## Lexical Elements

    The Jack language includes five types of terminal elements (tokens).

    - keyword: 'class' | 'constructor' | 'function' | 'method' | 'field' | 
               'static' | 'var' | 'int' | 'char' | 'boolean' | 'void' | 'true' |
               'false' | 'null' | 'this' | 'let' | 'do' | 'if' | 'else' | 
               'while' | 'return'
    - symbol: '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' | 
              '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
    - integerConstant: A decimal number in the range 0-32767.
    - StringConstant: '"' A sequence of Unicode characters not including 
                      double quote or newline '"'
    - identifier: A sequence of letters, digits, and underscore ('_') not 
                  starting with a digit. You can assume keywords cannot be
                  identifiers, so 'self' cannot be an identifier, etc'.

    ## Program Structure

    A Jack program is a collection of classes, each appearing in a separate 
    file. A compilation unit is a single class. A class is a sequence of tokens 
    structured according to the following context free syntax:
    
    - class: 'class' className '{' classVarDec* subroutineDec* '}'
    - classVarDec: ('static' | 'field') type varName (',' varName)* ';'
    - type: 'int' | 'char' | 'boolean' | className
    - subroutineDec: ('constructor' | 'function' | 'method') ('void' | type) 
    - subroutineName '(' parameterList ')' subroutineBody
    - parameterList: ((type varName) (',' type varName)*)?
    - subroutineBody: '{' varDec* statements '}'
    - varDec: 'var' type varName (',' varName)* ';'
    - className: identifier
    - subroutineName: identifier
    - varName: identifier

    ## Statements

    - statements: statement*
    - statement: letStatement | ifStatement | whileStatement | doStatement | 
                 returnStatement
    - letStatement: 'let' varName ('[' expression ']')? '=' expression ';'
    - ifStatement: 'if' '(' expression ')' '{' statements '}' ('else' '{' 
                   statements '}')?
    - whileStatement: 'while' '(' 'expression' ')' '{' statements '}'
    - doStatement: 'do' subroutineCall ';'
    - returnStatement: 'return' expression? ';'

    ## Expressions
    
    - expression: term (op term)*
    - term: integerConstant | stringConstant | keywordConstant | varName | 
            varName '['expression']' | subroutineCall | '(' expression ')' | 
            unaryOp term
    - subroutineCall: subroutineName '(' expressionList ')' | (className | 
                      varName) '.' subroutineName '(' expressionList ')'
    - expressionList: (expression (',' expression)* )?
    - op: '+' | '-' | '*' | '/' | '&' | '|' | '<' | '>' | '='
    - unaryOp: '-' | '~' | '^' | '#'
    - keywordConstant: 'true' | 'false' | 'null' | 'this'
    
    Note that ^, # correspond to shiftleft and shiftright, respectively.
    """
    MAP_KEYWORDS = {
        'class': "CLASS", 'constructor': "CONSTRUCTOR", 'function': "FUNCTION",
        'method': "METHOD", 'field': "FIELD", 'static': "STATIC", 'var': "VAR",
        'int': "INT", 'char': "CHAR", 'boolean': "BOOLEAN", 'void': "VOID",
        'true': "TRUE", 'false': "FALSE", 'null': "NULL", 'this': "THIS",
        'let': "LET", 'do': "DO", 'if': "IF", 'else': "ELSE",
        'while': "WHILE", 'return': "RETURN"
    }

    MAP_SYMBOLS = {'{', '}', '(', ')', '[', ']', '.', ',', ';', '+',
               '-', '*', '/', '&', '|', '<', '>', '=', '~', '^', '#'}




    def __init__(self, input_stream: typing.TextIO) -> None:
        """Opens the input stream and gets ready to tokenize it.

        Args:
            input_stream (typing.TextIO): input stream.
        """
        # Your code goes here!
        # A good place to start is to read all the lines of the input:
        # input_lines = input_stream.read().splitlines()
        input_text = input_stream.read()
        clean_text = JackTokenizer.remove_comments(input_text)
        self.tokens = []
        i = 0
        while i < len(clean_text):
            token, next_i = self._extract_next_token(clean_text, i)
            if token is not None:
                self.tokens.append(token)
            i = next_i

        self.current_index = -1
        self.current_token = None

    def _extract_next_token(self, text: str, i: int):
        # 1. skip whitespace
        while i < len(text) and text[i].isspace():
            i += 1
        if i >= len(text):
            return None, i

        # 2. string constant
        if text[i] == '"':
            j = i + 1
            while j < len(text) and text[j] != '"':
                j += 1
            return text[i:j+1], j + 1

        # 3. symbol 
        if text[i] in self.MAP_SYMBOLS:
            return text[i], i + 1

        # 4. integer constant
        if text[i].isdigit():
            j = i
            while j < len(text) and text[j].isdigit():
                j += 1
            return text[i:j], j

        # 5. identifier / keyword
        if text[i].isalpha() or text[i] == '_':
            j = i
            while j < len(text) and (text[j].isalnum() or text[j] == '_'):
                j += 1
            return text[i:j], j

        
        return text[i], i + 1


    @staticmethod
    def remove_comments(text: str) -> str:
        """Removes all comments from the source code.

        Args:
            text (str): source code text.

        Returns:
            str: text without comments.
        """
        result = []
        i = 0
        in_string = False
        
        while i < len(text):
            # Handle string literals
            if text[i] == '"' and not in_string:
                in_string = True
                result.append(text[i])
                i += 1
            elif text[i] == '"' and in_string:
                in_string = False
                result.append(text[i])
                i += 1
            # Handle // line comment
            elif not in_string and i + 1 < len(text) and text[i:i+2] == '//':
                while i < len(text) and text[i] != '\n':
                    i += 1
            # Handle /* block comment */
            elif not in_string and i + 1 < len(text) and text[i:i+2] == '/*':
                i += 2
                while i + 1 < len(text) and text[i:i+2] != '*/':
                    i += 1
                i += 2  # Skip */
            else:
                result.append(text[i])
                i += 1
        
        return ''.join(result)



    def has_more_tokens(self) -> bool:
        """Do we have more tokens in the input?

        Returns:
            bool: True if there are more tokens, False otherwise.
        """
        # Your code goes here!
        return self.current_index + 1 < len(self.tokens)

    def advance(self) -> None:
        """Gets the next token from the input and makes it the current token. 
        This method should be called if has_more_tokens() is true. 
        Initially there is no current token.
        """
        # Your code goes here!
        self.current_index += 1
        self.current_token = self.tokens[self.current_index]


    def token_type(self) -> str:
        """
        Returns:
            str: the type of the current token, can be
            "KEYWORD", "SYMBOL", "IDENTIFIER", "INT_CONST", "STRING_CONST"
        """
        # Your code goes here!
        if self.current_token is None:
            return ""
        if self.current_token in JackTokenizer.MAP_KEYWORDS:
            return "KEYWORD"
        elif self.current_token in JackTokenizer.MAP_SYMBOLS:
            return "SYMBOL"
        elif self.current_token.isdigit() and 0 <= int(self.current_token) <= 32767:
            return "INT_CONST"
        elif self.current_token.startswith('"') and self.current_token.endswith('"'):
            return "STRING_CONST"
        else:
            return "IDENTIFIER"

    def keyword(self) -> str:
        """
        Returns:
            str: the keyword which is the current token.
            Should be called only when token_type() is "KEYWORD".
            Can return "CLASS", "METHOD", "FUNCTION", "CONSTRUCTOR", "INT", 
            "BOOLEAN", "CHAR", "VOID", "VAR", "STATIC", "FIELD", "LET", "DO", 
            "IF", "ELSE", "WHILE", "RETURN", "TRUE", "FALSE", "NULL", "THIS"
        """
        # Your code goes here!
        if self.current_token is None:
            return ""
        return JackTokenizer.MAP_KEYWORDS[self.current_token]

    def symbol(self) -> str:
        """
        Returns:
            str: the character which is the current token.
            Should be called only when token_type() is "SYMBOL".
            Recall that symbol was defined in the grammar like so:
            symbol: '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' | 
              '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
        """
        # Your code goes here!
        return self.current_token if self.current_token else "" 
    def identifier(self) -> str:
        """
        Returns:
            str: the identifier which is the current token.
            Should be called only when token_type() is "IDENTIFIER".
            Recall that identifiers were defined in the grammar like so:
            identifier: A sequence of letters, digits, and underscore ('_') not 
                  starting with a digit. You can assume keywords cannot be
                  identifiers, so 'self' cannot be an identifier, etc'.
        """
        # Your code goes here!
        return self.current_token if self.current_token else ""

    def int_val(self) -> int:
        """
        Returns:
            str: the integer value of the current token.
            Should be called only when token_type() is "INT_CONST".
            Recall that integerConstant was defined in the grammar like so:
            integerConstant: A decimal number in the range 0-32767.
        """
        # Your code goes here!
        return int(self.current_token) if self.current_token else 0

    def string_val(self) -> str:
        """
        Returns:
            str: the string value of the current token, without the double 
            quotes. Should be called only when token_type() is "STRING_CONST".
            Recall that StringConstant was defined in the grammar like so:
            StringConstant: '"' A sequence of Unicode characters not including 
                      double quote or newline '"'
        """
        # Your code goes here!
        if self.current_token and self.current_token.startswith('"') and self.current_token.endswith('"'):
            return self.current_token[1:-1]  # Remove quotes
        return ""



        
