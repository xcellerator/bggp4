.PHONY: all, test

all:
	nasm -f bin -o a a.asm

test:
	@python3 a
	@sha256sum a 4
	@rm 4
	@ls -la a
