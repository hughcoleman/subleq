### assembler

This tool can be used to assemble an Assembly-like program into a SUBLEQ binary program.

###### Instructions

The assembler supports a total of fourteen different instructions.

**Operation**|**Effect**|**Additional Notes**
:-----:|:-----:|:-----:
`noop`| |Do nothing.
`subleq <o1> <o2> <o3>`|`o1 o2 o3`|Directly loads the subleq instruction `o1 o2 o3` into memory.
`add <o1> <o2>`|`o1 $X ip+3`<br />`$X o2 ip+3`<br />`$X $X ip+3`|Adds the contents of `o1` to `o2`. 
`sub <o1> <o2>`|`o1 o2 ip+3`|Subtracts the contents of `o1` from `o2`.
`zer <addr>`|`addr addr ip+3`|Zeroes memory at address `addr`. 
`mov <src> <dest>`|`dest dest ip+3`<br />`src $X ip+3`<br />`$X dest ip+3`<br />`$X $X ip+3`|Moves the contents of address `src` to address `dest`.
`jmp <addr>`|`$X $X addr`|Jumps to address `addr`. 
`beq <o> <addr>`|`o $X ip+6`<br />`$X $X ip+9`<br />`$X $X ip+3`<br />`$X o addr`|Jumps to address `addr` if `o` is zero.
`cmp <o1> <o2> <dest>`|`mov o1 $Y`<br />`sub o2 $Y`<br />`beq $Y dest`|Jumps to address `dest` addr if `o1` = `o2`. 
`in <addr>`|`-1 addr ip+3`|Reads a single byte from standard input into memory at address `addr`.
`out <addr>`|`addr -1 ip+3`|Sends the value in memory at address `addr` to standard output.
`int <n>`|`n`|Directly loads the integer `n` into memory.
`bytes "<s>"`|`s`|Directly loads the bytes in the string `s` into memory. Use backslashes to escape quotes.
`halt`|`-1 -1 0`|Halts the program. 

Labels can also be used to refer to locations in memory by name.

###### Usage

To use the assembler, run `assembler.py` in your terminal and supply the path to the Assembly file as the first parameter.

```sh
python assembler.py <assembly file>
```

###### Additional Command-Line Options

The assembler accepts some command-line flags to modify its behaviour.

 - `--out` or `-o` can be used to specify an output file.
 - `--size <n>` or `-s <n>` can be used to set the number of bytes allocated to each memory location value in the program binary.