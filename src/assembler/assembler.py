#!/usr/bin/env python
# -*- coding: utf-8 -*-

# assembler.py
# Copyright (c) 2020 Hugh Coleman
#
# This file is part of hughcoleman/subleq, a collection of tools for working
# with SUBLEQ one-instruction set computers. It is released under the MIT 
# License (see LICENSE.)

import re
import argparse

# RegEx matching valid character set for the source file. String literals in
# the source are not subject to this restriction.
SOURCE_CHARSET = re.compile(r"[\s\\\"a-zA-Z\-0-9:+-_,\[\];#<\.>=\$]")

# These are the valid "control characters" that the preprocessor will recognize.
VALID_ESCAPE_CHARACTERS = ["\\"]
VALID_QUOTATION_CHARACTERS = ["\""]
VALID_EOL_COMMENT_CHARACTERS = [";"]
VALID_TOKEN_DELIMITER = [" ", ","]

# These are the valid directive statements that the preprocessor will recognize.
VALID_INCLUDE_DIRECTIVES = ["#include"]
VALID_PRAGMA_DIRECTIVES = ["#set"]

class AssemblySyntaxError(Exception):
    pass

class PreprocessorMacroParseError(Exception):
    pass

def preprocess(program):
    """Preprocess a SUBLEQ assembly program.

    This function accepts a SUBLEQ assembly program as input, and will remove
    empty lines, remove comments, and will expand relevant macros. It will
    return a list of tokens which can be used by the assembler."""

    tokens = []

    for line, statement in enumerate(program.split('\n')):
        token = ""
        quoted = False
        column = 0
        while column < len(statement):
            character = statement[column]

            # Complain if there are any illegal characters in the source.
            if (not quoted) and (not bool(SOURCE_CHARSET.match(character))):
                raise AssemblySyntaxError(
                    f"\n\n\t{statement}\n" +\
                    f"\t{' '*column}^\n" +\
                    f"Unexpected character \"{character}\" on line {line}."
                )

            # If an escape character is encountered...
            elif (character in VALID_ESCAPE_CHARACTERS):
                # and it is in a double-quoted string, add the proceeding 
                # character literal to the current token.
                if quoted:
                    token = token + statement[column + 1]
                    column = column + 1 # also skip that column

                # if it is not quoted, complain.
                else:
                    raise AssemblySyntaxError(
                        f"\n\n\t{statement}\n" +\
                        f"\t{' '*column}^\n" +\
                        f"Unexpected escape character on line {line}."
                    )

            # If a valid (ie. not escaped) quotation mark is encountered, toggle
            # the current quoted status.
            elif (character in VALID_QUOTATION_CHARACTERS):
                quoted = not quoted

            # If we encounter a semicolon, and we are not currently in a quoted
            # string literal, the rest of the line is a comment. Ignore it all.
            elif (not quoted) and (character in VALID_EOL_COMMENT_CHARACTERS):
                break

            # If we encounter a space, and we are not currently in a quoted
            # string literal, then we are at a token boundary. Append the
            # current token to the global list, and clear the current token.
            elif (not quoted) and (character in VALID_TOKEN_DELIMITER):
                if token:
                    tokens.append(token)
                    token = ""

            # Otherwise, the current character can be appended to the current 
            # token.
            else:
                token += character

            # Then, continue parsing the next character.
            column = column + 1

        # The very last token in every line will not get added to the global
        # list, so it is manually appended here.
        if token:
            tokens.append(token)

        # If, at the end of the line, we are for some reason in a quoted string,
        # complain.
        if quoted:
            raise AssemblySyntaxError(
                f"\n\n\t{statement}\n" +\
                f"\t{' '*column}^\n" +\
                f"Unexpected EOL on line {line}."
            )

    # Now, we can parse the #include statements (which include an external
    # source file.)
    directives = {}

    index = 0
    while (index < len(tokens)):
        token = tokens[index]

        if (token in VALID_INCLUDE_DIRECTIVES):
            # Extract the name of the external file to include.
            include = tokens[index + 1][1:-1]

            try:
                with open(include) as fh:
                    external = fh.read()

                # Preprocess the external source file, and insert the processed
                # tokens into the "master" tokens list.
                _, external_tokens = preprocess(external)
                tokens[index:index+2] = external_tokens
            except FileNotFoundError:
                raise PreprocessorMacroParseError(
                    f"\n\nCould not include external source file <{include}>."
                )

        elif (token in VALID_PRAGMA_DIRECTIVES):
            # Extract the pragmatic statement.
            key, value = tokens[index + 1].split('=')
            directives[key] = value

            tokens.pop(index)   # remove the directive from the tokens list
            tokens.pop(index)   # remove the statement from the tokens list
            index = index - 1   # decrement the index (otherwise statements may
                                # be skipped.)

        index = index + 1

    return (directives, tokens)

# This dictionary lists the valid assembly operations supported by this
# assembler. Each key references a tuple, containing (a) the number of
# parameters consumed by that operation, and (b) the number of **SUBLEQ** memory
# cells that the assembled operation will consume.
OPERATIONS = {
    'noop': (0, 3),
    'subleq': (3, 3),
    'add': (2, 9),
    'sub': (2, 3),
    'zer': (1, 3),
    'mov': (2, 12),
    'jmp': (1, 3),
    'beq': (2, 12),
    'cmp': (3, 27),
    'in': (1, 3),
    'out': (1, 3),
    'int': (1, 1),
    'bytes': (1, None),
    'halt': (0, 3)
}

class AssemblerError(Exception):
    pass

def assemble(tokens, directives={}):
    """ Assemble an assembly program into the format recognized by a
    SUBLEQ-based one-instruction set computer. The following assembly
    instructions are supported.

        noop
            No operation.
        subleq <a> <b> <c>
            SUBLEQ <a> <b> <c>.
        add <a> <b>
            Add <a> to <b>. <a> is not destroyed.
        sub <a> <b>
            Subtract <a> from <b>. <a> is not destroyed.
        zer <a>
            Zero <a>.
        mov <a> <b>
            Copy from <a> to <b>.
        jmp <address>
            Jump to <address>.
        beq <x> <address>
            Jump to <address> if <x> is zero.
        cmp <a> <b> <address>
            Jump to <address> if <a> equals <b>.
        in <address>
            Read a value from standard input into <address>.
        out <address>
            Output the contents of <address>.
        int <a>
            Directly load the integer <a> into memory.
        bytes "<a>"
            Directly load the bytes of <a> into memory.
        halt
            Halt.
    """

    memory = []

    # First, we insert a "preamble" - SUBLEQ bytecode and memory locations that
    # are referenced by the assembler itself.

    preamble = [3, 3, 6, 0, 0, 0]
    memory.extend(preamble)

    X, Y = 3, 4       # addresses of assembler-accessible memory locations

    # Then, we can loop over our program and separate instructions from labels.
    # We also store the address of each label.

    ip = len(preamble)  # keep track of the running instruction pointer / count
    sequence = []       # list of statements in execution sequence order
    labels = {          # dictionary of program labels (label: address)
        "$X": 3,            # duplicate references to assembler memory cells, so
                            # that they can be used within the Assembly source
        "$Y": 4,            
        "$Z": 5
    }
    constants = {}      # keep a dictionary of the inline constants so that they
                        # can be allocated a location at the end of the source.


    index = 0
    while (index < len(tokens)):
        token = tokens[index]

        # If the token is a supported operation, extract it and its parameters
        # and append that information to the sequence list.
        if (token in OPERATIONS.keys()):
            arguments, size = OPERATIONS[token]
            
            # Increment the assembler-tracked instruction pointer by the "size"
            # of this instruction in compiled form.
            if size:
                ip += size
            else:
                assert (token == "bytes")
                ip += len(tokens[index + 1])

            # Now, extract the parameters.
            parameters = []
            for _ in range(arguments):
                parameter = tokens[index + 1]

                if (parameter.startswith('[') and parameter.endswith(']')):
                    if (parameter not in constants.keys()):
                        constants[parameter] = None

                parameters.append(parameter)
                index = index + 1

            sequence.append([token, parameters])

        # If the token is a label, extract it and store its address.
        elif (token.endswith(":")):
            label = token[:-1]
            if (label in labels.keys()):
                raise AssemblerError(
                    f"\n\nLabel \"{label}\" declared multiple times."
                )
            labels[label] = ip

        # Otherwise, compain.
        else:
            raise AssemblerError(f"\n\nUnrecognized token {token}.")

        index = index + 1

    # Now, we can allocate memory locations for the constants.
    for constant in constants.keys():
        if (constant[1:-1]).isdigit():
            constants[constant] = (int(constant[1:-1]), ip)
        elif (constant[1:-1]).startswith("0x"):
            constants[constant] = (int(constant[1:-1], 16), ip)
        elif (constant[1:-1] in labels.keys()):
            constants[constant] = (labels[constant[1:-1]], ip)
        else:
            raise AssemblerError(f"\n\nUnrecognized constant {constant}.")

        ip = ip + 1

    # Now, we can replace each assembly instruction with its synthesized "pure
    # SUBLEQ" form.
    ip = len(preamble)

    for instruction, parameters in sequence:
        # First, we parse the parameters to ensure they are all direct
        # addresses. The following "formats" are recognized.
        # 
        #  - <label>
        #  - <label>+offset
        #  - <literal address>
        #  - [<constant>]
        for position, parameter in enumerate(parameters):
            if (parameter in labels.keys()):
                parameters[position] = labels[parameter]
            elif (parameter.startswith('[') and parameter.endswith(']')):
                _, address = constants[parameter]
                parameters[position] = address
            elif (parameter.isdigit()):
                parameters[position] = int(parameter)
            elif ('+' in parameter):
                label, offset = parameter.split('+')
                parameters[position] = labels[label] + int(offset)
            else:
                parameters[position] = [ord(c) for c in parameter]

        # Now, we can write the instructions to memory.

        if instruction == 'noop':
            ip = ip + 3; memory.extend([X, X, ip])

        elif instruction == 'subleq':
            o1, o2, o3 = parameters
            ip = ip + 3; memory.extend([o1, o2, o3])

        elif instruction == 'add':
            o1, o2 = parameters
            ip = ip + 3; memory.extend([o1, X, ip])
            ip = ip + 3; memory.extend([X, o2, ip])
            ip = ip + 3; memory.extend([X, X, ip]) 

        elif instruction == 'sub':
            o1, o2 = parameters
            ip = ip + 3; memory.extend([o1, o2, ip])

        elif instruction == 'zer':
            addr, = parameters
            ip = ip + 3; memory.extend([addr, addr, ip])

        elif instruction == 'mov':
            src, dest = parameters
            ip = ip + 3; memory.extend([dest, dest, ip])
            ip = ip + 3; memory.extend([src, X, ip])
            ip = ip + 3; memory.extend([X, dest, ip])
            ip = ip + 3; memory.extend([X, X, ip])

        elif instruction == 'jmp':
            addr, = parameters
            ip = ip + 3; memory.extend([X, X, addr])

        elif instruction == 'beq':
            o, addr = parameters
            ip = ip + 3; memory.extend([o, X, ip + 3])
            ip = ip + 3; memory.extend([X, X, ip + 6])
            ip = ip + 3; memory.extend([X, X, ip])
            ip = ip + 3; memory.extend([X, o, addr])

        elif instruction == 'cmp':
            o1, o2, addr = parameters
            # mov <A> Y
            ip = ip + 3; memory.extend([Y, Y, ip])
            ip = ip + 3; memory.extend([o1, X, ip])
            ip = ip + 3; memory.extend([X, Y, ip])
            ip = ip + 3; memory.extend([X, X, ip])
            # sub <B> Y
            ip = ip + 3; memory.extend([o2, Y, ip])
            # beq Y <C>
            ip = ip + 3; memory.extend([Y, X, ip + 3])
            ip = ip + 3; memory.extend([X, X, ip + 6])
            ip = ip + 3; memory.extend([X, X, ip])
            ip = ip + 3; memory.extend([X, Y, addr])
        
        elif instruction == 'in':
            addr, = parameters
            ip = ip + 3; memory.extend([-1, addr, ip])

        elif instruction == 'out':      
            addr, = parameters
            ip = ip + 3; memory.extend([addr, -1, ip])

        elif instruction == 'int':
            n, = parameters
            ip = ip + 1; memory.extend([n])

        elif instruction == 'bytes':
            s, = parameters
            ip = ip + len(s); memory.extend(s)

        elif instruction == 'halt':
            ip = ip + 3; memory.extend([-1, -1, 0])

    # We can also write all constants to program memory. This includes the
    # program entry point (if it has been configured using the #set ENTRY=XYZ)
    # directive. 
    if ("ENTRY" in directives.keys()):
        memory[2] = labels[directives["ENTRY"]]

    for constant, (value, address) in constants.items():
        while (len(memory) <= address):
            memory.append(0)

        memory[address] = value

    return memory

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("program", help="program file to assemble")
    parser.add_argument("-o", "--out", help="assembled output file",
        default="a.out")
    parser.add_argument("-s", "--size", type=int, default=4,
        help="size (in bytes) of integers to write to program binary")

    args = parser.parse_args()

    with open(args.program) as fh:
        program = fh.read()

    directives, tokens = preprocess(program)
    memory = assemble(tokens, directives=directives)

    with open(args.out, "wb") as fh:
        for v in memory:
            fh.write(v.to_bytes(args.size, byteorder="big", signed=True))