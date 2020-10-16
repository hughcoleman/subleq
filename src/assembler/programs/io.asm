;------------------------------------------------------------------------------
; io.asm
; A demonstration of the I/O statement offered by the SUBLEQ assembler
;------------------------------------------------------------------------------

#set ENTRY=main

m: int 32

main:
  out m                 ; print the value at m (32)
  in m                  ; read a value into m
  out m                 ; print the value at m (the input value)
  halt