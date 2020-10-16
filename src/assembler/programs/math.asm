;------------------------------------------------------------------------------
; math.asm
; A demonstration of the supported mathematical instructions 
;------------------------------------------------------------------------------

#set ENTRY=main

main:
  add a b
  out b                 ; prints b + a (11)
  
  sub c d
  out d                 ; prints c - d (-5)
  
  halt

a: int 3
b: int 8
c: int 17
d: int 12