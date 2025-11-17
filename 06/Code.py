"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""


class Code:
    """Translates Hack assembly language mnemonics into binary codes."""
    
    @staticmethod
    def dest(mnemonic: str) -> str:
        """
        Args:
            mnemonic (str): a dest mnemonic string.

        Returns:
            str: 3-bit long binary code of the given mnemonic.
        """
        # Your code goes here!
        dest_table = {
            'null': '000',
            'M': '001',
            'D': '010',
            'MD': '011',
            'A': '100',
            'AM': '101',
            'AD': '110',
            'AMD': '111'
        }
        return dest_table.get(mnemonic,000)  # Default to '000'  if mnemonic not found   

    @staticmethod
    def comp(mnemonic: str) -> str:
        """
        Args:
            mnemonic (str): a comp mnemonic string.

        Returns:
            str: the binary code of the given mnemonic.
        """
        # Your code goes here!
        comp_table = {
          "0":"110101010",
        "1":"110111111",
        "-1":"110111010",
        "D":"110001100",
        "A":"110110000",
        "!D":"110001101",
        "!A":"110110001",
        "-D":"110001111",
        "-A": "110110011",
        "D+1": "110011111",
        "A+1": "110110111",
        "D-1": "110001110",
        "A-1": "110110010",
        "D+A": "110000010",
        "D-A": "110010011",
        "A-D": "110000111",
        "D&A": "110000000",
        "D|A": "110010101",
        "M": "111110000",
        "!M": "111110001",
        "-M": "111110011",
        "M+1": "111110111",
        "M-1": "111110010",
        "D+M": "111000010",
        "D-M": "111010011",
        "M-D": "111000111",
        "D&M": "111000000",
        "D|M": "111010101",
        "A<<": "010100000",
        "D<<": "010110000",
        "M<<": "011100000",
        "A>>": "010000000",
        "D>>": "010010000",
        "M>>": "011000000"
        } 
        return comp_table.get(mnemonic)  
      

    @staticmethod
    def jump(mnemonic: str) -> str:
        """
        Args:
            mnemonic (str): a jump mnemonic string.

        Returns:
            str: 3-bit long binary code of the given mnemonic.
        """
        # Your code goes here!
        jump_table = {
            'null': '000',
            'JGT': '001',
            'JEQ': '010',
            'JGE': '011',
            'JLT': '100',
            'JNE': '101',
            'JLE': '110',
            'JMP': '111'
        }
        return jump_table.get(mnemonic, '000')  # Default to '000' if mnemonic not found
