#!/usr/bin/env python3

import sys

prg_fname = sys.argv[1]
d64_fname = sys.argv[2]

offset = 0x15002

with open('template.d64','rb') as f:
    template = bytearray(f.read())

with open(prg_fname, 'rb') as f:
    prg = f.read()

template[offset:offset+len(prg)] = prg

with open(d64_fname,'wb') as f:
    f.write(template)
