## Purpose
This file tells an AI coding assistant how to be immediately productive in this repo (Hack assembler, nand2tetris project, project 06).

Keep edits small and local. The project is a straightforward Python assembler with several TODOs; most work is focused in `Code.py`, `Parser.py`, `SymbolTable.py` and `Main.py`.

## Big-picture architecture
- Entry point: `Main.py` — drives assembling of one or more `.asm` files into `.hack` files. `Main.assemble_file(input_file, output_file)` is the main unit to implement.
- Parser: `Parser.py` — reads cleaned lines from the `.asm` file, exposes parser API: `has_more_commands()`, `advance()`, `command_type()` (returns one of `"A_COMMAND"`, `"C_COMMAND"`, `"L_COMMAND"`), `symbol()`, `dest()`, `comp()`, `jump()`.
- Symbol table: `SymbolTable.py` — stores predefined symbols and user labels/variables, provides `add_entry(symbol, address)`, `contains(symbol)`, `get_address(symbol)`.
- Code translation: `Code.py` — converts mnemonics to binary: `dest(mnemonic)` -> 3 bits, `comp(mnemonic)` -> 7 bits (a + cccccc), `jump(mnemonic)` -> 3 bits.

Dataflow summary: Main -> Parser (iterate commands) -> SymbolTable (resolve labels/vars) -> Code (translate mnemonics) -> write binary lines to `.hack` (same folder as input; filename.ext .asm -> .hack).

## Project-specific conventions & expectations
- Input files: any `.asm` file under the project (see example programs in `add/`, `max/`, `pong/`, `rect/`, `shift/`). The assembler writes `<input_basename>.hack` next to the `.asm` file.
- Parser API returns raw mnemonics (e.g., `dest()` returns `'D'` or `''`), not binary. `Code.py` is responsible for mapping mnemonics -> fixed-width binary strings.
- `SymbolTable` should be pre-populated with Hack predefined symbols (SP, LCL, ARG, THIS, THAT, R0-R15, SCREEN, KBD). Variable allocation starts at RAM address 16.
- C-instruction binary format expected by the tests: `111` + comp(7) + dest(3) + jump(3). Implementations should return strings of `0`/`1` with the correct width.

## How to run and developer workflows
- Unix (project provided wrapper): `./Assembler <path>` — calls `python3 Main.py $*` (script `Assembler` exists but is a shell script; it won't run on Windows).
- Windows / cross-platform (explicit):
  - Open PowerShell in project folder and run: `python Main.py <path>` where `<path>` is a single `.asm` file or a directory. Example: `python Main.py add` will assemble all `.asm` files in `add/`.
- Output: For each `Xxx.asm`, the assembler creates `Xxx.hack` in the same directory.
- Makefile: `make` is provided to `chmod a+x *` on Unix. Not required on Windows; prefer running Python directly on Windows.

## Implementation hints (concrete, repository-specific)
- Parser: strip whitespace and comments (`//`), skip blank lines, and maintain a list/iterator of cleaned commands. `symbol()` should return the symbol string WITHOUT `@` or parentheses.
- SymbolTable: populate predefined symbols and provide a next-free variable pointer starting at 16 for unknown symbols encountered in A-commands.
- Code: return fixed-width binary strings. Use the nand2tetris spec mappings (comp includes the a-bit). Example contract: `Code.dest('M') -> '001'`, `Code.jump('JGT') -> '001'`, `Code.comp('D+1') -> '0011111'` (implement per spec).
- Main.assemble_file: two-pass approach is expected: pass 1 to record label (L_COMMAND) addresses into SymbolTable, pass 2 to translate instructions (A/C commands), allocating variable addresses as needed.

## Files to open first (quick links)
- `Main.py` — orchestrator and CLI usage
- `Parser.py` — parser API and TODOs
- `Code.py` — mnemonic->binary mapping stubs
- `SymbolTable.py` — symbol storage and allocation
- `Makefile` / `Assembler` — how the authors expect the tool to be run on Unix vs Windows

## Examples from repo (useful for tests)
- `add/Add.asm` -> expected machine code in `Add.hack` (use as a quick smoke test)
- `shift/Shift.hack` is present as an example output for the `shift` program; compare produced output to this file when verifying correctness.

## Non-goals / things not to assume
- There are no unit tests in the repo; rely on the sample `.asm` programs for validation.
- Do not change public function names or signatures — other files import the classes directly (Main imports Parser, Code, SymbolTable).

If anything is unclear or you'd like me to also implement the TODOs in `Parser.py` / `SymbolTable.py` / `Code.py` / `Main.py`, tell me which file to start with and I will implement and run a quick validation using the sample programs.
