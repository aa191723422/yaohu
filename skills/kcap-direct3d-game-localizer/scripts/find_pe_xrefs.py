#!/usr/bin/env python3
"""Find direct x86 references to strings stored at PE file offsets."""
from __future__ import annotations
import argparse,struct
from pathlib import Path
import pefile
from capstone import CS_ARCH_X86,CS_MODE_32,Cs
def main():
    parser=argparse.ArgumentParser(); parser.add_argument("exe",type=Path); parser.add_argument("offsets",nargs="+"); parser.add_argument("--context",type=int,default=32); args=parser.parse_args()
    pe=pefile.PE(str(args.exe),fast_load=False); data=args.exe.read_bytes(); image_base=pe.OPTIONAL_HEADER.ImageBase; code_section=next(section for section in pe.sections if section.Characteristics&0x20000000); code_start=code_section.PointerToRawData; code_end=code_start+code_section.SizeOfRawData; code_va=image_base+code_section.VirtualAddress; disassembler=Cs(CS_ARCH_X86,CS_MODE_32)
    for value in args.offsets:
        offset=int(value,0); va=image_base+pe.get_rva_from_offset(offset); needle=struct.pack("<I",va); hits=[]; cursor=code_start
        while True:
            hit=data.find(needle,cursor,code_end)
            if hit<0: break
            hits.append(hit); cursor=hit+1
        print(f"offset=0x{offset:X} va=0x{va:X} xrefs={len(hits)}")
        for hit in hits:
            start=max(code_start,hit-args.context); end=min(code_end,hit+args.context); start_va=code_va+start-code_start; print(f"  file_xref=0x{hit:X}")
            for instruction in disassembler.disasm(data[start:end],start_va): print(f"    {instruction.address:08X}: {instruction.mnemonic:7} {instruction.op_str}")
if __name__=="__main__": main()
