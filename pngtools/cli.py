#!/bin/env python3

"""pngtools cli"""

from os.path import join, expanduser
import cmd2
from .lib import (
    ERROR_CODE,
    acropalypse,
    get_errors_of_chunk,
    parse_idat,
    write_png,
    print_chunks,
    fix_chunk,
    create_ihdr_chunk,
    remove_chunk_by_type,
    create_iend_chunk,
    extract_sub_chunks,
    try_decompress,
    extract_idat,
    get_data_of_chunk,
    get_type_of_chunk,
    decode_ihdr,
    read_file,
)
from .bmp import create_bmp
from .ppm import convert_rgba_to_rgb, create_ppm

PATH_HISTORY = join(expanduser("~"), ".pngtools_history.dat")


class CLI(cmd2.Cmd):
    """pngtools CLI"""

    chunks = []

    def __init__(self):
        super().__init__(
            persistent_history_file=PATH_HISTORY,
        )
        self.prompt = "pngtools> "
        self.debug = True

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
    delete_chunk_parser.add_argument("index", type=int, help="Index to delete")

    @cmd2.with_argparser(delete_chunk_parser)
    def do_delete_chunk(self, args):
        """delete chunk file"""
        index = int(args.index)
        if len(self.chunks) > index:
            self.chunks.pop(index)
        else:
            print(f"Invalid index {index} to delete")

    fix_chunk_parser = cmd2.Cmd2ArgumentParser()
    fix_chunk_parser.add_argument("index", type=int, help="Index to fix")

    @cmd2.with_argparser(fix_chunk_parser)
    def do_fix_chunk(self, args):
        """fix chunk file"""
        index = int(args.index)
        if len(self.chunks) >= index:
            self.chunks[index] = fix_chunk(self.chunks[index])
        else:
            print("Invalid index to fix")

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
                print("Invalid index to show data")
        else:
            print("No chunks to show data")

    show_data_uncompressed_parser = cmd2.Cmd2ArgumentParser()
    show_data_uncompressed_parser.add_argument(
        "index", type=int, help="Index to show uncompressed data"
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

    do_extract_sub_chunks_parser = cmd2.Cmd2ArgumentParser()
    do_extract_sub_chunks_parser.add_argument(
        "index", type=int, help="Index to extract sub chunks"
    )

    @cmd2.with_argparser(do_extract_sub_chunks_parser)
    def do_extract_sub_chunks(self, args):
        """show data of chunk"""
        index = int(args.index)
        if len(self.chunks) > 0:
            if len(self.chunks) >= index:
                self.sub_chunks(index)
            else:
                print("Invalid index")
        else:
            print("No chunks")

    def sub_chunks(self, index):
        """Extract sub chunk"""
        chunks_to_add = extract_sub_chunks(self.chunks.pop(index))
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

    acropalypse_parser = cmd2.Cmd2ArgumentParser()
    acropalypse_parser.add_argument("origin_width", type=int, help="Original width")
    acropalypse_parser.add_argument("origin_height", type=int, help="Original height")

    @cmd2.with_argparser(acropalypse_parser)
    def do_acropalypse(self, args):
        """Try acropalypse"""
        origin_width = int(args.origin_width)
        origin_height = int(args.origin_height)
        (
            _width,
            _height,
            bit_depth,
            color_type,
            _,
            _,
            _,
        ) = decode_ihdr(get_data_of_chunk(self.chunks[0]))
        indexes_iend = [
            i
            for i, one_chunk in enumerate(self.chunks)
            if get_type_of_chunk(one_chunk) == b"IEND"
        ]
        if len(indexes_iend) <= 1:
            print("No IEND chunk found")
            return
        print("More than one IEND chunk !")
        self.chunks = [
            chunk
            for i, chunk in enumerate(self.chunks)
            if ERROR_CODE["WRONG_CRC"] in get_errors_of_chunk(chunk)
        ]
        self.chunks = extract_sub_chunks(self.chunks[0])
        print("Hidden chunks:")
        print_chunks(self.chunks)
        data = acropalypse(
            self.chunks, origin_width, origin_height, bit_depth, color_type
        )
        if color_type == 6:
            # RGBA to RGB - we remove the 4th value of each pixel
            data = convert_rgba_to_rgb(data)
        output_file = "acropalypse.ppm"
        create_ppm(output_file, origin_width, origin_height, data)
        print(f"Output file: {output_file}")

    bitmap_parser = cmd2.Cmd2ArgumentParser()
    bitmap_parser.add_argument("filename", help="Output filename")

    @cmd2.with_argparser(bitmap_parser)
    def do_create_bmp(self, args):
        """Create a bmp from the chunks"""
        out_filename = args.filename
        data_idat = b"".join(extract_idat(self.chunks))
        (
            width,
            height,
            bit_depth,
            color_type,
            _,
            _,
            _,
        ) = decode_ihdr(get_data_of_chunk(self.chunks[0]))
        decomp = try_decompress(data_idat)
        data = parse_idat(decomp, width, height, bit_depth, color_type)
        create_bmp(out_filename, width, height, bit_depth, color_type, data)

    ppm_parser = cmd2.Cmd2ArgumentParser()
    ppm_parser.add_argument("filename", help="Output filename")

    @cmd2.with_argparser(ppm_parser)
    def do_create_ppm(self, args):
        """Create a ppm from the chunks"""
        out_filename = args.filename
        data_idat = b"".join(extract_idat(self.chunks))
        (
            width,
            height,
            bit_depth,
            color_type,
            _,
            _,
            _,
        ) = decode_ihdr(get_data_of_chunk(self.chunks[0]))
        decomp = try_decompress(data_idat)
        data = parse_idat(decomp, width, height, bit_depth, color_type)
        if color_type == 6:
            # RGBA to RGB - we remove the 4th value of each pixel
            data = convert_rgba_to_rgb(data)
        create_ppm(out_filename, width, height, data, binary=True)

    def do_exit(self, _args):
        """Exit the program"""
        return True


def cli_main():
    """Main function to run the CLI"""
    import sys  # pylint: disable=import-outside-toplevel

    c = CLI()
    sys.exit(c.cmdloop())


if __name__ == "__main__":
    cli_main()
