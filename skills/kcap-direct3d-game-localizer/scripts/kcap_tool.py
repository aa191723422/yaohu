#!/usr/bin/env python3
"""Index, extract, and rebuild KCAP archives."""
from __future__ import annotations
import argparse,csv,hashlib,struct
from dataclasses import dataclass
from pathlib import Path
MAGIC=b"KCAP"; ENTRY_SIZE=84; NAME_SIZE=64
@dataclass
class Entry:
    index:int; name_raw:bytes; hash1:int; hash2:int; offset:int; size:int; flags:int
    @property
    def name(self): return self.name_raw.split(b"\0",1)[0].decode("cp932")
    def serialize(self,offset,size): return self.name_raw+struct.pack("<5I",self.hash1,self.hash2,offset,size,self.flags)
def safe_path(name):
    path=Path(*name.replace("\\","/").split("/"))
    if path.is_absolute() or ".." in path.parts: raise ValueError(f"Unsafe archive path: {name}")
    return path
def read_index(path):
    with path.open("rb") as stream:
        if stream.read(4)!=MAGIC: raise ValueError("Not a KCAP archive")
        count=struct.unpack("<I",stream.read(4))[0]; entries=[]
        for index in range(count):
            raw=stream.read(ENTRY_SIZE)
            if len(raw)!=ENTRY_SIZE: raise ValueError(f"Truncated entry {index}")
            entries.append(Entry(index,raw[:NAME_SIZE],*struct.unpack_from("<5I",raw,NAME_SIZE)))
    return entries,8+count*ENTRY_SIZE
def digest(data): return hashlib.sha256(data).hexdigest()
def index_pack(pack,output):
    entries,_=read_index(pack)
    with pack.open("rb") as source,output.open("w",encoding="utf-8-sig",newline="") as target:
        writer=csv.writer(target); writer.writerow(["entry_index","archive_path","offset","size","flags","sha256"])
        for entry in entries:
            source.seek(entry.offset); data=source.read(entry.size)
            writer.writerow([entry.index,entry.name,entry.offset,entry.size,f"{entry.flags:08X}",digest(data)])
def extract(pack,output,prefix):
    entries,_=read_index(pack); normalized=prefix.upper().replace("/","\\") if prefix else None
    with pack.open("rb") as source:
        for entry in entries:
            if normalized and not entry.name.upper().startswith(normalized): continue
            source.seek(entry.offset); data=source.read(entry.size)
            if len(data)!=entry.size: raise ValueError(f"Truncated payload: {entry.name}")
            destination=output/safe_path(entry.name); destination.parent.mkdir(parents=True,exist_ok=True); destination.write_bytes(data)
def rebuild(source_pack,output,replacements):
    entries,header_end=read_index(source_pack); physical=sorted(entries,key=lambda item:item.offset)
    if physical and physical[0].offset!=header_end: raise ValueError("First payload does not start after the KCAP index")
    payloads={}
    with source_pack.open("rb") as source:
        for entry in entries:
            candidate=replacements/safe_path(entry.name) if replacements else None
            if candidate and candidate.is_file(): payloads[entry.index]=candidate.read_bytes()
            else: source.seek(entry.offset); payloads[entry.index]=source.read(entry.size)
    positions={}; cursor=header_end
    for entry in physical: payload=payloads[entry.index]; positions[entry.index]=(cursor,len(payload)); cursor+=len(payload)
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open("wb") as target:
        target.write(MAGIC); target.write(struct.pack("<I",len(entries)))
        for entry in entries: target.write(entry.serialize(*positions[entry.index]))
        for entry in physical: target.write(payloads[entry.index])
def main():
    parser=argparse.ArgumentParser(); commands=parser.add_subparsers(dest="command",required=True)
    cmd=commands.add_parser("index"); cmd.add_argument("pack",type=Path); cmd.add_argument("output",type=Path)
    cmd=commands.add_parser("extract"); cmd.add_argument("pack",type=Path); cmd.add_argument("output",type=Path); cmd.add_argument("--prefix")
    cmd=commands.add_parser("rebuild"); cmd.add_argument("source",type=Path); cmd.add_argument("output",type=Path); cmd.add_argument("--replacements",type=Path)
    args=parser.parse_args()
    if args.command=="index": index_pack(args.pack,args.output)
    elif args.command=="extract": extract(args.pack,args.output,args.prefix)
    else: rebuild(args.source,args.output,args.replacements)
if __name__=="__main__": main()
