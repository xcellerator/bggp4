NASM=nasm
FNAME=elf

.PHONY: all
all:
	@$(NASM) -f bin -o $(FNAME) $(FNAME).asm
	@chmod +x $(FNAME)
	@strace ./$(FNAME) || /bin/true
	@sudo chmod 777 4
	@echo
	@sha256sum $(FNAME) 4
	@rm 4
	@echo
	@ls -la $(FNAME)
