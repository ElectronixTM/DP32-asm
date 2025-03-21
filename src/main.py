#!/usr/bin/python3

from lexer import DPLexer
from preprocessor import DPPreprocessor
from parser import DPParser
from assembler import Assembler
from abstracts import Operation, Label, RawData
from argparse import ArgumentParser

def assemble(text: str) -> bytearray:
    """
    Assembles file directly to bytecode
    """
    l = DPLexer()
    p = DPParser()
    preproc = DPPreprocessor()
    ast = p.parse(
            preproc.preprocess(
                l.tokenize(text)
                )
            )
    assert (isinstance(ast, list)
            and all(isinstance(i, (Operation, Label, RawData)) for i in ast))
    a = Assembler()
    return a.assemble(ast)

def bytearray_to_lab(barr: bytearray) -> str:
    """
    Cast byte array to appropriate for lab format
    """
    result = ""
    while len(barr):
        command, barr = barr[:4], barr[4:]
        result += ("X\""
                   + command[:2].hex()
                   + "_"
                   + command[2:].hex()
                   + '"\n')
    return result

def main():
    parser = ArgumentParser()
    parser.add_argument("file", help="file to assemble")
    parser.add_argument(
            "-f",
            "--format",
            default='bin',
            help=(
                "fromat for output. Can be `bin` or `lab`. "
                "`bin` will generate binary file, `lab` will "
                "generate output in appropriate for vhdl format")
            )
    parser.add_argument(
            "-o",
            "--output",
            default="out.bin",
            help="file to store result to"
            )
    args = parser.parse_args()

    with open(args.file, 'r') as f:
        text = f.read()
    result = assemble(text)
    if args.format == "bin":
        with open(args.output, 'wb') as f:
            f.write(result)
    elif args.format == "lab":
        out = bytearray_to_lab(result)
        with open(args.output, 'w') as f:
            f.write(out)

if __name__ == "__main__":
    main()
