#!/usr/bin/python3

from lexer import DPLexer
from preprocessor import DPPreprocessor
from parser import DPParser
from assembler import Assembler
from abstracts import Operation, Label, RawData
from argparse import ArgumentParser
from errorwatcher import TrackedErrorsList, TrackedError, ErrorWatcher

def report_error(error: TrackedError, source: str):
    error_watcher = ErrorWatcher()
    location = error_watcher.get_info_by_id(error.failed_on._id)
    lines = source.split('\n')
    line = lines[location.lineno-1]
    err_index: int = location.index - len("\n".join(lines[:location.lineno-1]) + '\n')
    print(f"Error accured on line {location.lineno} "
          f"at index {location.index}. Started from:")
    print("\t"+line)
    print("\t"+" "*err_index + "^")
    print("[ERROR MSG]:", error.msg, end="\n\n")

def report_errors_list(errors: TrackedErrorsList, source: str):
    print(errors.text.center(40, "_"))
    for error in errors.exceptions:
        report_error(error, source)

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
    if not ast:
        raise ValueError("Syntax analysis failed. Aborting assembling stage")
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
                   + '",\n')
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
    result = None
    try:
        result = assemble(text)
    except TrackedError as e:
        report_error(e, text)
        print("Couldn't perform assembling due to the error")
        return
    except TrackedErrorsList as e:
        report_errors_list(e, text)
        print("Couldn't perform assembling due to listed errors")
        return
    except Exception as e:
        print(e)
        return
    if args.format == "bin":
        with open(args.output, 'wb') as f:
            f.write(result)
    elif args.format == "lab":
        out = bytearray_to_lab(result)
        with open(args.output, 'w') as f:
            f.write(out)

if __name__ == "__main__":
    main()
