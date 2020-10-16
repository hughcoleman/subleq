#!/usr/bin/env python
# -*- coding: utf-8 -*-

# emulator.py
# Copyright (c) 2020 Hugh Coleman
#
# This file is part of hughcoleman/subleq, a collection of tools for working
# with SUBLEQ one-instruction set computers. It is released under the MIT 
# License (see LICENSE.)

import sys
import argparse

class VirtualMachine:
    """ A virtual machine of the SUBLEQ one-instruction set computer. """
    def run(self):
        while True:
            a, b, c = self.memory[self.ip : self.ip + 3]
            self.ip += 3

            if (self.args.debugger):
                # print the current instruction pointer and command to execute
                print(f"\n[{hex(self.ip-3)[2:].zfill(4)}] {a} {b} {c} ")

                instruction = input("> ")
                tokens = instruction.split(" ")
                if (tokens[0].lower() in ["e", "execute"]):
                    pass
                elif (tokens[0].lower() in ["s", "skip"]):
                    continue
                elif (tokens[0].lower() in ["m", "modify"]):
                    a, b, c = [int(v) for v in tokens[1].split(",")]

            if (a == -1) and (b == -1):
                if (self.args.debugger):
                    print(f"Terminated with status {c}.")
                return c
            elif (a == -1):
                # If the input queue is empty, then prompt the user for input
                # via stdin.
                if not self.inputs:
                    if (self.args.debugger):
                        print("\n\n[!] The input queue is empty; prompting " +\
                              "for additional input.")

                    self.inputs.extend( [ord(c) for c in input("\n> ") ] )

                    # Optionally null-terminate all input that is passed to the
                    # machine.
                    if self.args.null_terminate_input:
                        self.inputs.extend( [0] )

                self.memory[b] = self.inputs.pop(0)
            elif (b == -1):
                if self.args.ascii:
                    print(chr(self.memory[a]), end='')
                else:
                    print(self.memory[a])
            else:
                self.memory[b] -= self.memory[a]
                if self.memory[b] <= 0:
                    self.ip = c

    def __init__(self, memory=[], args=None):
        self.memory = memory
        self.ip = 0
        self.inputs = []
        self.args = args

if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument("program", help="binary program to execute")
    parser.add_argument("-n", "--null-terminate-input", 
        help="null-terminate all input strings supplied via standard input",
        action="store_true"
    )
    parser.add_argument("-a", "--ascii", 
        help="print machine output as ascii",
        action="store_true"
    )
    parser.add_argument("-d", "--debugger",
        help="enable debugging tools",
        action="store_true"
    )
    parser.add_argument("-s", "--size", type=int, default=4,
        help="size (in bytes) of integers to read from program binary")

    args = parser.parse_args()

    with open(args.program, "rb") as fh:
        memory = []
        while (v := fh.read(args.size)):
            memory.append(int.from_bytes(v, byteorder="big", signed=True))

    vm = VirtualMachine(memory=memory, args=args)
    vm.run()
