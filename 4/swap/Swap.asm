// This file is part of nand2tetris, as taught in The Hebrew University, and
// was written by Aviv Yaish. It is an extension to the specifications given
// [here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
// as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
// Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).

// The program should swap between the max. and min. elements of an array.
// Assumptions:
// - The array's start address is stored in R14, and R15 contains its length
// - Each array value x is between -16384 < x < 16384
// - The address in R14 is at least >= 2048
// - R14 + R15 <= 16383
//
// Requirements:
// - Changing R14, R15 is not allowed.

// Put your code here.
// ---------------------------------------------------------
// swapMinMax.asm
// Finds min and max in array [R14 ... R14+R15-1] and swaps them
// Constraints: R14 = base address (unchanged), R15 = length (unchanged)
// ---------------------------------------------------------

// ---------------------------------------------------------
// Step 0: Handle edge cases
// If length < 2, do nothing (no swap needed)
// ---------------------------------------------------------
    @R15        // load length
    D=M
    @END        // if length < 2 => jump to END
    D=D-1       // D = length-1
    D;JLT       // if length-1 < 0 (i.e. length ==0), skip
    @R15
    D=M
    @END
    D=D-1
    D;JEQ       // if length ==1 , skip

// ---------------------------------------------------------
// Step 1: Initialize i=0, read first element as initial max and min
// ---------------------------------------------------------
    // i = 0
    @R0
    M=0

    // addr = R14 + i  (which is R14 + 0 = R14)
    @R14
    D=M        // D = base address
    @R13
    M=D        // R13 = current element address

    // read arr[0] into D
    @R13
    A=M
    D=M        // D = arr[0]

    // maxVal = arr[0]
    @R1
    M=D
    // maxIndex = 0
    @R2
    M=0

    // minVal = arr[0]
    @R3
    M=D
    // minIndex = 0
    @R4
    M=0

    // i = 1 (we'll continue loop from the second element)
    @R0
    M=1

// ---------------------------------------------------------
// Step 2: Main scan loop
// Loop condition: while i < length
// ---------------------------------------------------------
(LOOP)
    // Check if i >= length -> if yes, exit loop
    @R0
    D=M        // D = i
    @R15
    D=D-M      // D = i - length
    @AFTER_LOOP
    D;JGE      // if i - length >= 0 => i >= length => done

    // -------------------------------------------------
    // Compute address of arr[i] into R13:
    // R13 = R14 + i
    // -------------------------------------------------
    @R14
    D=M        // D = base
    @R0
    D=D+M      // D = base + i
    @R13
    M=D        // R13 = &arr[i]

    // load arr[i] into D
    @R13
    A=M
    D=M        // D = arr[i]

    // We'll need arr[i] several times, so store it in temp R5
    @R5
    M=D        // R5 = currentValue

    // -------------------------------------------------
    // Check if currentValue > maxVal
    // if (arr[i] - maxVal) > 0  ==> update max
    // -------------------------------------------------
    @R5
    D=M        // D = arr[i]
    @R1
    D=D-M      // D = arr[i] - maxVal
    @CHECK_MIN
    D;JLE      // if arr[i] <= maxVal skip update

    // Update maxVal = arr[i]
    @R5
    D=M
    @R1
    M=D
    // maxIndex = i
    @R0
    D=M
    @R2
    M=D

(CHECK_MIN)
    // -------------------------------------------------
    // Check if currentValue < minVal
    // if (arr[i] - minVal) < 0 ==> update min
    // -------------------------------------------------
    @R5
    D=M        // D = arr[i]
    @R3
    D=D-M      // D = arr[i] - minVal
    @INC_I
    D;JGE      // if arr[i] >= minVal skip update

    // Update minVal = arr[i]
    @R5
    D=M
    @R3
    M=D
    // minIndex = i
    @R0
    D=M
    @R4
    M=D

(INC_I)
    // i = i + 1
    @R0
    M=M+1

    // repeat loop
    @LOOP
    0;JMP

// ---------------------------------------------------------
// Step 3: After loop: we have maxIndex (R2), minIndex (R4)
// Now perform the swap:
// temp = arr[maxIndex]
// arr[maxIndex] = arr[minIndex]
// arr[minIndex] = temp
// ---------------------------------------------------------
