"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import os
import sys
import typing
from SymbolTable import SymbolTable
from Parser import Parser
from Code import Code


def assemble_file(
        input_file: typing.TextIO, output_file: typing.TextIO) -> None:
    """Assembles a single file.

    Args:
        input_file (typing.TextIO): the file to assemble.
        output_file (typing.TextIO): writes all output to this file.
    """
    # Your code goes here!
    # A good place to start is to initialize a new Parser object:
    # parser = Parser(input_file)
    # Note that you can write to output_file like so:
    # output_file.write("Hello world! \n")
    parser = Parser(input_file)
    symbol_table = SymbolTable()   
    parser.table = symbol_table 

    # First pass: add label symbols to the symbol table
    # we  start with rom 0 because all rom adresses start from 0

    rom_address = 0     
    while parser.has_more_commands():
        parser.advance()
        t= parser.command_type()
        if t == "L_COMMAND":
            label = parser.symbol()
            symbol_table.add_entry(label, rom_address)
        elif parser.command_type() == "A_COMMAND" or parser.command_type() == "C_COMMAND":
            rom_address += 1

    # Second pass: translate commands

    parser.current_command_index= -1  # reset parser to beginning
    
    while parser.has_more_commands():
        parser.advance()
        if parser.command_type() == "A_COMMAND":
            if parser.current_command== "@OUPTUT_FIRST":
                value= "0000000000010000"
                output_file.write(value+"\n")
                continue
            value= parser.a_instruction_value()
            output_file.write(value+"\n")
                              
        elif parser.command_type() == "C_COMMAND":
            dest = parser.dest()
            comp = parser.comp()
            jump = parser.jump()
            comp_bits = Code.comp(comp)
            dest_bits = Code.dest(dest) 
            jump_bits = Code.jump(jump)
            output_file.write(f"1{comp_bits}{dest_bits}{jump_bits}\n")



if "__main__" == __name__:
    # Parses the input path and calls assemble_file on each input file.
    # This opens both the input and the output files!
    # Both are closed automatically when the code finishes running.
    # If the output file does not exist, it is created automatically in the
    # correct path, using the correct filename.
    if not len(sys.argv) == 2:
        sys.exit("Invalid usage, please use: Assembler <input path>")
    argument_path = os.path.abspath(sys.argv[1])
    if os.path.isdir(argument_path):
        files_to_assemble = [
            os.path.join(argument_path, filename)
            for filename in os.listdir(argument_path)]
    else:
        files_to_assemble = [argument_path]
    for input_path in files_to_assemble:
        filename, extension = os.path.splitext(input_path)
        if extension.lower() != ".asm":
            continue
        output_path = filename + ".hack"
        with open(input_path, 'r') as input_file, \
                open(output_path, 'w') as output_file:
            assemble_file(input_file, output_file)
