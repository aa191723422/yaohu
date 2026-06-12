#!/usr/bin/env python3
"""Probe ANSI glyph rendering with GetGlyphOutlineA on Windows."""
from __future__ import annotations
import argparse,ctypes,json
from ctypes import wintypes
from pathlib import Path
FR_PRIVATE=0x10; GGO_GRAY8_BITMAP=6; GDI_ERROR=0xFFFFFFFF
class FIXED(ctypes.Structure): _fields_=[("fract",wintypes.WORD),("value",ctypes.c_short)]
class MAT2(ctypes.Structure): _fields_=[("eM11",FIXED),("eM12",FIXED),("eM21",FIXED),("eM22",FIXED)]
class POINT(ctypes.Structure): _fields_=[("x",wintypes.LONG),("y",wintypes.LONG)]
class GLYPHMETRICS(ctypes.Structure): _fields_=[("gmBlackBoxX",wintypes.UINT),("gmBlackBoxY",wintypes.UINT),("gmptGlyphOrigin",POINT),("gmCellIncX",ctypes.c_short),("gmCellIncY",ctypes.c_short)]
class LOGFONTA(ctypes.Structure): _fields_=[("lfHeight",wintypes.LONG),("lfWidth",wintypes.LONG),("lfEscapement",wintypes.LONG),("lfOrientation",wintypes.LONG),("lfWeight",wintypes.LONG),("lfItalic",wintypes.BYTE),("lfUnderline",wintypes.BYTE),("lfStrikeOut",wintypes.BYTE),("lfCharSet",wintypes.BYTE),("lfOutPrecision",wintypes.BYTE),("lfClipPrecision",wintypes.BYTE),("lfQuality",wintypes.BYTE),("lfPitchAndFamily",wintypes.BYTE),("lfFaceName",ctypes.c_char*32)]
def ansi_word(character,encoding):
    raw=character.encode(encoding)
    if len(raw)==1: return raw[0]
    if len(raw)==2: return raw[0]<<8|raw[1]
    raise ValueError(f"Expected one ANSI character: {character!r}")
def main():
    parser=argparse.ArgumentParser(); parser.add_argument("font",type=Path); parser.add_argument("family"); parser.add_argument("characters"); parser.add_argument("--encoding",default="cp936"); parser.add_argument("--charset",type=int,default=134); parser.add_argument("--height",type=int,default=32); args=parser.parse_args()
    gdi32=ctypes.WinDLL("gdi32",use_last_error=True); user32=ctypes.WinDLL("user32",use_last_error=True)
    if not gdi32.AddFontResourceExW(str(args.font.resolve()),FR_PRIVATE,0): raise ctypes.WinError(ctypes.get_last_error())
    dc=user32.GetDC(0); logfont=LOGFONTA(); logfont.lfHeight=args.height; logfont.lfWeight=400; logfont.lfCharSet=args.charset; logfont.lfOutPrecision=7; logfont.lfQuality=2; logfont.lfPitchAndFamily=0x31; logfont.lfFaceName=args.family.encode("ascii"); font=gdi32.CreateFontIndirectA(ctypes.byref(logfont)); old=gdi32.SelectObject(dc,font); matrix=MAT2(FIXED(0,1),FIXED(0,0),FIXED(0,0),FIXED(0,1)); rows=[]
    try:
        for character in args.characters:
            metrics=GLYPHMETRICS(); code=ansi_word(character,args.encoding); size=gdi32.GetGlyphOutlineA(dc,code,GGO_GRAY8_BITMAP,ctypes.byref(metrics),0,None,ctypes.byref(matrix)); rows.append({"character":character,"code":f"0x{code:04X}","success":size!=GDI_ERROR,"bitmap_size":None if size==GDI_ERROR else size,"width":metrics.gmBlackBoxX,"height":metrics.gmBlackBoxY})
    finally:
        gdi32.SelectObject(dc,old); gdi32.DeleteObject(font); user32.ReleaseDC(0,dc); gdi32.RemoveFontResourceExW(str(args.font.resolve()),FR_PRIVATE,0)
    print(json.dumps(rows,ensure_ascii=False))
if __name__=="__main__": main()
