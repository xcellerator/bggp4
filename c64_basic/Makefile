.PHONEY=all

ASM=nasm
C64=x64

IN=basic.asm
OUT=basic.prg
DISK=disk.d64

all:
	$(ASM) -f bin -o $(OUT) $(IN)
	python3 insert_prg.py $(OUT) $(DISK)

run:
	$(C64) -autoload $(DISK)
