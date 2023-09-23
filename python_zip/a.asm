; Python ZIP

org 0x0

PKZipFileHeader:
db 0x50, 0x4b, 0x03, 0x04                                       ; Signature
times 22 db 0x58
dd 0x00000000                                                   ; Filename Size

Contents:
db "import os;print('4');os.system('cp a 4')"

PKZipStartOfCentralDirectory:
db 0x50, 0x4b, 0x01, 0x02                                       ; Signature
times 6 db 0x58
dw 0x0000                                                       ; Compression Method (NONE)
times 8 db 0x58
dd PKZipStartOfCentralDirectory - Contents                      ; Compressed Size
dd PKZipStartOfCentralDirectory - Contents                      ; Uncompressed Size
dw PKZipEndOfCentralDirectory - Filename                        ; Filename Size
dw 0x0000                                                       ; Extra Field Length
dw 0x0000                                                       ; File Comment Length
times 8 db 0x58
dd PKZipFileHeader                                              ; PKZipFileHeader Offset

Filename:
db "__main__.py"

PKZipEndOfCentralDirectory:
db 0x50, 0x4b, 0x05, 0x06                                       ; Signature
times 6 db 0x58
dw 0x0001                                                       ; Number of Entries (0x1)
dd PKZipEndOfCentralDirectory - PKZipStartOfCentralDirectory    ; Size Of Central Directory
dd PKZipStartOfCentralDirectory                                 ; Offset to Start of Central Directory
times 2 db 0x58
