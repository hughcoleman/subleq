;------------------------------------------------------------------------------
; strings.asm
; A demonstration of strings and byte-types.
;------------------------------------------------------------------------------

#set ENTRY=main

message: bytes "Hello, world!"

main:
  out message+0
  out message+1
  out message+2
  out message+3
  out message+4
  out message+5
  out message+6
  out message+7
  out message+8
  out message+9
  out message+10
  out message+11
  out message+12
  halt