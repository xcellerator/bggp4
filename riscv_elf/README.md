# RISC-V Elf

To test (on a RISC-V machine), just run `make`.

Total size: 142 bytes.

```sh
$ make
rm -f 4
nasm -f bin -o elf elf.asm
./elf || /bin/true

sha256sum elf 4
001709c49a83c14cdad71d0182d62bdb33a3f43647d867299208a6a899deb422  elf
001709c49a83c14cdad71d0182d62bdb33a3f43647d867299208a6a899deb422  4

ls -la elf
-rwxrwxr-x 1 ubuntu ubuntu 142 Aug 19 17:27 elf
```
