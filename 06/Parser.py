"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
import SymbolTable


class Parser:
    """Encapsulates access to the input code. Reads an assembly program
    by reading each command line-by-line, parses the current command,
    and provides convenient access to the commands components (fields
    and symbols). In addition, removes all white space and comments.
    """

    def __init__(self, input_file: typing.TextIO) -> None:
        """Opens the input file and gets ready to parse it.

        Args:
            input_file (typing.TextIO): input file.
        """
        # Your code goes here!
        # A good place to start is to read all the lines of the input:
        # input_lines = input_file.read().splitlines()
        input_lines = input_file.read().splitlines()
        self.commands = []
        for line in input_lines:
            # Remove comments
            line = line.split('//')[0]
            # Remove whitespace
            line = line.strip()
            if line:
                self.commands.append(line)
        self.current_command_index = -1 # start with -1 so that advance() sets it to 0 on first call
        self.table = SymbolTable.SymbolTable()
        self.number_of_symbols = 16  # Next available RAM address for variables



    def has_more_commands(self) -> bool:
        """Are there more commands in the input?

        Returns:
            bool: True if there are more commands, False otherwise.
        """
        # Your code goes here!
        return self.current_command_index + 1 < len(self.commands)

    def advance(self) -> None:
        """Reads the next command from the input and makes it the current command.
        Should be called only if has_more_commands() is true.
        """
        # Your code goes here!
        if self.has_more_commands():
            self.current_command_index += 1
            self.current_command = self.commands[self.current_command_index]

    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current command:
            "A_COMMAND" for @Xxx where Xxx is either a symbol or a decimal number
            "C_COMMAND" for dest=comp;jump
            "L_COMMAND" (actually, pseudo-command) for (Xxx) where Xxx is a symbol
        """
        # Your code goes here!
        if self.current_command.startswith('@'):
            return "A_COMMAND"
        elif self.current_command.startswith('(') and self.current_command.endswith(')'):
            return "L_COMMAND"
        else:
            return "C_COMMAND"

    def symbol(self) -> str:
        """
        Returns:
            str: the symbol or decimal Xxx of the current command @Xxx or
            (Xxx). Should be called only when command_type() is "A_COMMAND" or 
            "L_COMMAND".
        """
        # Your code goes here!
        if self.command_type() == "A_COMMAND":
            return self.current_command[1:]  # Remove '@'
        elif self.command_type() == "L_COMMAND":
            return self.current_command[1:-1]  # Remove '(' and ')'
        else:
            raise ValueError("symbol() should be called only for A_COMMAND or L_COMMAND")
    def dest(self) -> str:
        """
        Returns:
            str: the dest mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        # Your code goes here!
        if self.command_type() != "C_COMMAND":
            raise ValueError("dest() should be called only for C_COMMAND")
        command = self.current_command
        # if "=" dont exist return null because there is no dest part
        if '=' in command:
            return self.current_command.split('=')[0].strip()
        else:
            return 'null'
        

    def comp(self) -> str:
        """
        Returns:
            str: the comp mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        # Your code goes here!
        if self.command_type() != "C_COMMAND":
            raise ValueError("comp() should be called only for C_COMMAND")
        command = self.current_command
        if '=' in command:
            return command.split('=')[1].split(';')[0].strip()
        else:
            return command.split(';')[0].strip()
        # If no '=' or ';' is found, return the entire command
        return command.strip()


    def jump(self) -> str:
        """
        Returns:
            str: the jump mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        # Your code goes here!
        # if there no ';' return null because there is no jump part so return 'null'
    
        if self.command_type() != "C_COMMAND":
            raise ValueError("jump() should be called only for C_COMMAND")
        command = self.current_command
        if ';' in command:
            return command.split(';')[1]
        else:
            return 'null'
        
    def a_instruction_value(self) -> str: 
        """ Returns: str: the value of the current A-instruction. Should be called only when commandType() is "A_COMMAND". """ # Your code goes here! symbol=self.symbol() if symbol.isdigit(): return self.padding(bin(int(symbol))[2:]) # Convert to binary and add zero padding else: if not self.table.contains(symbol): self.table.add_entry(symbol, self.number_of_symbols) self.number_of_symbols += 1 symbol = self.table.get_address(symbol) return self.padding(bin(address)[2:]) # Convert to binary and add zero padding    
        # Your code goes here!
        symbol = self.symbol()
        if symbol.isdigit():
            return self.padding(bin(int(symbol))[2:])  # Convert to binary and add zero padding
        else:
            if not self.table.contains(symbol):
                self.table.add_entry(symbol, self.number_of_symbols)
                self.number_of_symbols += 1
            symbol = self.table.get_address(symbol)
            return self.padding(bin(symbol )[2:])  # Convert to binary and add zero padding 
        


    def padding(self, binary: str) -> str:
        """
        Args:
            binary (str): the binary string to pad.
        Returns:
            str: the padded binary string.
        """
        return '0' * (16 - len(binary)) + binary    