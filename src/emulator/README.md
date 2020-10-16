### emulator

This tool can be used to emulate a SUBLEQ one-instruction set computer. 

The emulator operates following ["traditional" SUBLEQ rules](https://en.wikipedia.org/wiki/One-instruction_set_computer#Subtract_and_branch_if_less_than_or_equal_to_zero); repeatedly fetching, decoding, and executing `SUBLEQ` instructions *ad infinitum*. The emulator only breaks this cycle to respond to the following exceptions.

 - If the first parameter is `-1`, then a character is read from standard input and stored in the address given by the second. *The third parameter is ignored.*
 - If the second parameter is `-1`, then the integer stored at the address given by the first is written to standard output. *The third parameter is ignored.*
 - If both the first and second parameters are `-1`, then the machine halts with a status given by the third.

These three exceptions allow for seamless I/O with the emulated machine.

###### Usage

To use the emulator, run `emulator.py` in your terminal and supply the path to the binary program as the first parameter.

```sh
python emulator.py <binary file>
```

The `<binary file>` will be directly loaded into the emulator's memory at address 0.

###### Additional Command-Line Options

The emulator accepts some command-line flags to modify its behaviour.

 - `--null-terminate-input` or `-n` will null-terminate (ie. will append `\0` to) all input supplied via the emulator's standard input. This can be useful if your program expects null bytes to signify the end of input.
 - `--ascii` or `-a` can be used to print the computer's output as ASCII instead of raw numbers.
 - `--debugger` or `-d` will enable a rudimentary debugger.
 - `--size <n>` or `-s <n>` can be used to set the number of bytes allocated to each memory location value in the program binary.
