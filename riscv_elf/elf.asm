; DEFINES

%define ELFCLASS64                  0x02
%define ELFDATA2LSB                 0x01
%define ELFOSABI_SYSV               0x0
%define ET_EXEC                     0x0002
%define EM_RISCV                    0x00f3
%define EV_CURRENT                  0x00000001
%define EF_RISCV_RVC                0x0001
%define EF_RISCV_FLOAT_ABI_DOUBLE   0x0004
%define PT_LOAD                     0x00000001
%define PF_X                        0x1
%define PF_R                        0x4

%define LOADADDR                    0x00010000

; ELF Header

EhdrStart:

db 0x7f, 'ELF'          ; ELFMAG

CodeStart:
dd 0xf9c00513           ; li a0, -100           ; Arg1 (dirfd) = AT_FDCWD
dd 0x00000597           ; auipc a1, 0x0         ; a1 = pc + 0
dw 0x25b1               ; addiw a1, a1, +12     ; Arg2 (pathname) = pc + 12
dw 0xa829               ; c.j +0x1a             ; Jump to file offset 0x28

dw ET_EXEC              ; e_type
dw EM_RISCV             ; e_machine

TextStart:
db 0x34, 0x00
times 2 db 0x58
TextEnd:

dq LOADADDR + CodeStart ; e_entry
dq PhdrStart            ; e_phoff

dd 0x07d00613           ; li a2, 125            ; Arg3 (flags) = O_CREAT | O_WRONLY (125 = 101 | 24)
dw 0x4685               ; li a3, 1              ; Arg4 (mode) = O_WRONLY
dw 0xa031               ; c.j +0xc              ; Jump to file offset 0x3a

dd EF_RISCV_RVC | EF_RISCV_FLOAT_ABI_DOUBLE ; e_flags
dw EhdrEnd - EhdrStart  ; e_ehsize
dw PhdrEnd - PhdrStart  ; e_phentsize
dw 0x0001               ; e_phnum

dd 0x03800893           ; li a7, 56             ; Syscall = 56 (SYS_OPENAT)
dw 0xa82d               ; c.j +0x3a             ; Jump to file offset 0x78

EhdrEnd:

; Program Header

PhdrStart:

dd PT_LOAD              ; p_type
dd PF_X | PF_R          ; p_flags
dq 0x00000000           ; p_offset
dq LOADADDR             ; p_vaddr
dq LOADADDR             ; p_paddr
dq CodeEnd-CodeStart    ; p_filesz
dq CodeEnd-CodeStart    ; p_memsz
dq 0x00001000           ; p_align

PhdrEnd:

; Code

CodeCont:
; SYS_OPENAT(AT_FDCWD, "4", O_WRONLY|O_CREAT, O_WRONLY)
dd 0x00000073           ; ecall

; SYS_WRITE(FD, LOADADDR, BINARY_SIZE)
dw 0x15b1               ; addi a1, a1, -20      ; Arg2 (buf) = 0x10000
dw 0x0645               ; addi a2, a2, 17       ; Arg3 (len) = 142
dw 0x28a1               ; addiw a7, a7, 8       ; Syscall = 64 (SYS_WRITE)
dd 0x00000073           ; ecall

; SYS_EXIT(4)
dw 0x4511               ; li a0, 4              ; Arg1 (ret) = 4
dw 0x28f5               ; addiw a7, a7, 29      ; Syscall = 93 (SYS_EXIT)
dd 0x00000073           ; ecall
CodeEnd:
