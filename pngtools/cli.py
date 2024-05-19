# /bin/env python3

from os.path import join, expanduser
import cmd2
from .lib import (
    write_png,
    print_chunks,
    fix_chunk,
    create_ihdr_chunk,
    remove_chunk_by_type,
    create_iend_chunk,
    extract_sub_chunk,
    try_decompress,
    extract_idat,
    parse_idat,
    get_data_of_chunk,
    get_type_of_chunk,
    decode_ihdr,
    read_file,
)
from .bmp import create_bmp

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
        self.chunks = read_file(args.filename)

    complete_read_file = cmd2.Cmd.path_complete  # complete file path

    def do_show_chunks(self, _args):
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

    show_data_parser = cmd2.Cmd2ArgumentParser()
    show_data_parser.add_argument("index", type=int, help="Index to show data")

    @cmd2.with_argparser(show_data_parser)
    def do_show_data(self, args):
        """show data of chunk"""
        index = int(args.index)
        if len(self.chunks) > 0:
            if len(self.chunks) >= index:
                print(get_data_of_chunk(self.chunks[index]))
            else:
                print("Invalid index")
        else:
            print("No chunks")

    show_data_uncompressed_parser = cmd2.Cmd2ArgumentParser()
    show_data_uncompressed_parser.add_argument(
        "index", type=int, help="Index to show data"
    )

    @cmd2.with_argparser(show_data_uncompressed_parser)
    def do_show_data_uncompressed(self, args):
        """show uncrompressed data of chunk"""
        index = int(args.index)
        if len(self.chunks) > 0:
            if len(self.chunks) >= index:
                uncromp = get_data_of_chunk(self.chunks[index])
                data = try_decompress(uncromp)
                if data is not None:
                    print(data)
                else:
                    print("Decompression error")
            else:
                print("Invalid index")
        else:
            print("No chunks")

    do_extract_sub_chunk_parser = cmd2.Cmd2ArgumentParser()
    do_extract_sub_chunk_parser.add_argument(
        "index", type=int, help="Index to show data"
    )

    @cmd2.with_argparser(do_extract_sub_chunk_parser)
    def do_extract_sub_chunk(self, args):
        """show data of chunk"""
        index = int(args.index)
        if len(self.chunks) > 0:
            if len(self.chunks) >= index:
                self.extract_sub_chunk(index)
            else:
                print("Invalid index")
        else:
            print("No chunks")

    def extract_sub_chunk(self, index):
        """Extract sub chunk"""
        chunks_to_add = extract_sub_chunk(self.chunks.pop(index))
        if len(chunks_to_add) > 0:
            print("Extracted chunks:")
            print_chunks(chunks_to_add)
            for i, chunk in enumerate(chunks_to_add):
                self.chunks.insert(index + i, chunk)

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

    def do_show_ihdr(self, _args):
        """Show the IHDR chunk"""
        if self.chunks:
            indexes = [
                i
                for i, one_chunk in enumerate(self.chunks)
                if get_type_of_chunk(one_chunk) == b"IHDR"
            ]
            for index in indexes:
                print(f"IHDR chunk (index {index}):")
                data = get_data_of_chunk(self.chunks[index])
                (
                    width,
                    height,
                    bit_depth,
                    color_type,
                    compression_method,
                    filter_method,
                    interlace_method,
                ) = decode_ihdr(data)
                print("Width:", width)
                print("Height:", height)
                print("Bit depth:", bit_depth)
                print("Color type:", color_type)
                print("Compression method:", compression_method)
                print("Filter method:", filter_method)
                print("Interlace method:", interlace_method)

    def do_add_iend(self, _args):
        """Add an IEND chunk"""
        if self.chunks:
            self.chunks.append(create_iend_chunk())

    def do_acropalypse(self, _args):
        """Try acropalypse"""
        indexes_iend = [
            i
            for i, one_chunk in enumerate(self.chunks)
            if get_type_of_chunk(one_chunk) == b"IEND"
        ]
        if len(indexes_iend) > 1:
            print("More than one IEND chunk !")
            print("Removing all IEND chunks")
            self.chunks = remove_chunk_by_type(self.chunks, b"IEND")
            last_index = len(self.chunks) - 1
            print(f"Extracting data of last chunk ({last_index})")
            self.extract_sub_chunk(last_index)
            print("Final chunks:")
            print_chunks(self.chunks)

    bitmap_parser = cmd2.Cmd2ArgumentParser()
    bitmap_parser.add_argument("filename", help="Output filename")

    @cmd2.with_argparser(bitmap_parser)
    def do_create_bmp(self, args):
        """Test"""
        out_filename = args.filename
        data_idat = b"".join(extract_idat(self.chunks))
        (
            width,
            height,
            _,
            _,
            _,
            _,
            _,
        ) = decode_ihdr(get_data_of_chunk(self.chunks[0]))
        decomp = try_decompress(data_idat)
        create_bmp(width, height, out_filename, decomp)

    def do_exit(self, _args):
        """Exit the program"""
        return True


def cli_main():
    import sys

    c = CLI()
    sys.exit(c.cmdloop())


if __name__ == "__main__":
    cli_main()
