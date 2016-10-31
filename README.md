# MIPS Instruction Set Based CPU

This is an implementation for a simplified MIPS CPU using high level programming language. The considered simulator adopts a multi-cycle pipline processor to dynamically schedule instruction execution and employs caches in order to dynamically schedule instruction execution and employs caches in order to expedite memory access.

## Instruction Set
Generally speaking, this implementation supports the following MIPS instructions,

Instruction Class | Instruction Monemonic
------------------| ---------------------
Data Transfers    | LW, SW, L.D, S.D
Arithmetic / Logical | DADD, DADDI, DSUB, DSUBI, AND, ANDI, OR, ORI,<br/>ADD.D, MUL.D, DIV.D, SUB.D
Control           | J, BEQ, BNE
Special Purpose   | HLT(to stop fetching new instructions)

## Architecture
![alt text](README_FILES/01.png "CPU Architecture")

The overall architecture is shown in the above figure, taken from the project description of CMSC 611 spring 2014. Generally speaking, it includes two major parts: Memory and CPU. Memory includes instruction cache (I-Cache), data cache (D-Cache) and main memory. 
