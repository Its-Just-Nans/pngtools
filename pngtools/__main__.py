#!/usr/bin/env python3
"""pngtools"""

from os.path import exists, join, expanduser
import cmd2
from .__init__ import (
    split_png_chunks,
    write_png,
    print_chunks,
    fix_chunk,
    create_ihdr_chunk,
    remove_chunk_by_type,
    create_iend_chunk,
)

PATH_HISTORY = join(expanduser("~"), ".pngtools_history.dat")


class CLI(cmd2.Cmd):
    """pngtools CLI"""

    chunks = []

    def __init__(self):
        super().__init__(
            persistent_history_file=PATH_HISTORY,
        )
        self.prompt = "pngtools> "

    read_file_parser = cmd2.Cmd2ArgumentParser()
    read_file_parser.add_argument("filename", help="Path to the file")

    @cmd2.with_argparser(read_file_parser)
    def do_read_file(self, args):
        """Read a PNG file"""
        if exists(args.filename):
            self.chunks = split_png_chunks(args.filename)
        else:
            print("File does not exist")

    def do_show_chunks(self, args):
        """Show the chunks"""
        if self.chunks:
            print_chunks(self.chunks)
        else:
            print("No chunks to show")

    write_png_parser = cmd2.Cmd2ArgumentParser()
    write_png_parser.add_argument("filename", help="Output file name")

    @cmd2.with_argparser(write_png_parser)
    def do_write_png(self, args):
        """Write a PNG file"""
        filename = args.filename
        if self.chunks:
            write_png(self.chunks, filename)
        else:
            print("No chunks to write")

    delete_chunk_parser = cmd2.Cmd2ArgumentParser()
    delete_chunk_parser.add_argument("index", type=int, help="Index to remove")

    @cmd2.with_argparser(delete_chunk_parser)
    def do_delete_chunk(self, args):
        """delete chunk file"""
        index = int(args.index)
        if len(self.chunks) > index:
            self.chunks.pop(index)
        else:
            print("Invalid index")

    fix_chunk_parser = cmd2.Cmd2ArgumentParser()
    fix_chunk_parser.add_argument("index", type=int, help="Index to remove")

    @cmd2.with_argparser(fix_chunk_parser)
    def do_fix_chunk(self, args):
        """fix chunk file"""
        index = int(args.index)
        if len(self.chunks) >= index:
            self.chunks[index] = fix_chunk(self.chunks[index])
        else:
            print("Invalid index")

    replace_ihdr_parser = cmd2.Cmd2ArgumentParser()
    replace_ihdr_parser.add_argument("width", type=int, help="New width")
    replace_ihdr_parser.add_argument("height", type=int, help="New height")

    @cmd2.with_argparser(replace_ihdr_parser)
    def do_replace_ihdr(self, args):
        """Replace the IHDR chunk"""
        width = args.width
        height = args.height
        if self.chunks:
            self.chunks[0] = create_ihdr_chunk(width, height)

    remove_by_type_parser = cmd2.Cmd2ArgumentParser()
    remove_by_type_parser.add_argument("chunk_type", help="Type of chunk")

    @cmd2.with_argparser(remove_by_type_parser)
    def do_remove_by_type(self, args):
        """Remove chunks by type"""
        chunk_type = args.chunk_type.encode()
        if self.chunks:
            self.chunks = remove_chunk_by_type(self.chunks, chunk_type)

    def do_add_iend(self, args):
        """Add an IEND chunk"""
        if self.chunks:
            self.chunks.append(create_iend_chunk())

    def do_acropalypse(self, args):
        """Try acropalypse"""
        # check if there is two IEND chunks

    def do_exit(self, args):
        """Exit the program"""
        return True


if __name__ == "__main__":
    import sys

    c = CLI()
    sys.exit(c.cmdloop())
