;------------------------------------------------------------------------------
; addressing_modes.asm
; A demonstration of the addressing_modes offered by the SUBLEQ assembler
;------------------------------------------------------------------------------

#set ENTRY=main

m: int 17
n: int 189

main:
  ; print the value at address 12
  out 12

  ; print the value at label "m", which is 17
  out m
  
  ; print the value at label "m" with an offset of 1 (ie. label "n", so 189)
  out m+1

  ; print the address labelled by label "m"
  out [m]
  
  ; constants - print the literal value 0x22
  out [0x22]

  halt