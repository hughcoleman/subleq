;------------------------------------------------------------------------------
; print.asm
; A complex example demonstrating a program which will start at a given address
; and print values until it encounters a null (0) value.
;------------------------------------------------------------------------------

#set ENTRY=print

; load the message to print into memory
message: bytes "Hello, world! This is my long message."
         int 0 ; null-terminate

print:
    ; copy the start address into the "current address" memory location.
    ; notice that this is wrapped in square brackets; this ensures that the 
    ; literal numerical value of the start address is moved into the "current
    ; address" label. If it was not, the value 72 ('H') would be moved in
    ; instead.
    mov [message] print__current_address
    
    ; this loop drives the printing of the message
    print__loop:
        ; this is a "disassembled" MOV statement; essentially it moves the value
        ; that needs to be printed into the "output" memory location.
        print__current_address: int 0
                                int $X
                                int print__loop__continue
        print__loop__continue:
            sub $X print__output
            sub $X $X
    
    ; if the value to print is zero, quit.
    beq print__output print__end
    
    ; output, and then increment the address to print
    out print__output
    zer print__output
    add [1] print__current_address
    
    ; loop!
    jmp print__loop
    
    print__end:
        halt
    
    print__output: int 0
