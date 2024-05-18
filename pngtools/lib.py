from os import fstat
from os.path import exists
import zlib

ERROR_CODE = {
    "WRONG_LENGTH": "Wrong length",
    "EOF": "End of file",
    "WRONG_CRC": "Wrong CRC",
    "WRONG_TYPE": "Wrong type",
}

CHUNKS_TYPES = {
    b"IHDR": "Image header",
    b"PLTE": "Palette",
    b"IDAT": "Image data",
    b"IEND": "Image trailer",
    b"eXIf": "Exif data",
    b"cHRM": "Primary chromaticities",
    b"gAMA": "Image gamma",
    b"iCCP": "Embedded ICC profile",
    b"sBIT": "Significant bits",
    b"sRGB": "Standard RGB color space",
    b"bKGD": "Background color",
    b"hIST": "Image histogram",
    b"tRNS": "Transparency",
    b"pHYs": "Physical pixel dimensions",
    b"sPLT": "Suggested palette",
    b"tIME": "Image last-modification time",
    b"iTXt": "International textual data",
    b"tEXt": "Textual data",
    b"zTXt": "Compressed textual data",
}

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"

global offset
offset = 0


def read_from_file(fp, read_len):
    global offset
    if hasattr(fp, "read"):
        data = fp.read(read_len)
    else:
        data = fp[offset : offset + read_len]
        offset += read_len
    return data


def read_chunk(file, total_size):
    readed = read_from_file(file, 4)
    errors = []
    if readed == "":
        errors.append(ERROR_CODE["EOF"])
        return None, None, None, None, errors
    data_length = int.from_bytes(readed, byteorder="big")
    to_read = data_length
    if data_length > total_size:
        to_read = total_size - 3 * 4
        errors.append(ERROR_CODE["WRONG_LENGTH"])
    chunk_type = read_from_file(file, 4)
    if chunk_type not in CHUNKS_TYPES:
        errors.append(ERROR_CODE["WRONG_TYPE"])
    data = read_from_file(file, to_read)
    crc = read_from_file(file, 4)
    if crc != calculate_crc(chunk_type, data):
        errors.append(ERROR_CODE["WRONG_CRC"])
    return data_length, chunk_type, data, crc, errors


def try_dec(type_chunk):
    if type_chunk in CHUNKS_TYPES:
        return type_chunk.decode("utf-8")
    else:
        return "????"


def try_hex(a):
    try:
        return a.hex()
    except UnicodeDecodeError:
        return "????"


def get_by_type(chunks, type="IDAT"):
    return [one_chunk for one_chunk in chunks if one_chunk[1] == type]


def get_data_of_chunk(one_chunk):
    return one_chunk[2]


def extract_idat(chunks):
    return [
        get_data_of_chunk(one_chunk) for one_chunk in chunks if one_chunk[1] == b"IDAT"
    ]


def decode_phy(chunk):
    phy_chunk_data = get_data_of_chunk(chunk)
    x_pixels_per_unit = int.from_bytes(phy_chunk_data[0:4], byteorder="big")
    y_pixels_per_unit = int.from_bytes(phy_chunk_data[4:8], byteorder="big")
    unit_specifier = int.from_bytes(phy_chunk_data[8:9], byteorder="big")
    if unit_specifier == 0:
        # Units are unspecified or in inches, using default
        x_pixels_per_unit = 2835
        y_pixels_per_unit = 2835
    return x_pixels_per_unit, y_pixels_per_unit, unit_specifier


def extract_data(chunks):
    """extract data from IDAT chunks and try to decompress it"""
    data_idat = b"".join(extract_idat(chunks))
    return try_decompress(data_idat)


def reset_offset():
    global offset
    offset = 0


def read_broken_file(filename, force_idx=0):
    """Read a broken PNG file"""
    reset_offset()
    if exists(filename):
        with open(filename, "rb") as fp:
            file = fp.read()
        idxs = get_indices(file, PNG_MAGIC)
        if len(idxs) == 0:
            print("No PNG detected")
            return None
        print(f"PNG signatures detected at {idxs}")
        choosed_idx = force_idx if force_idx != 0 else idxs[0]
        return split_png_chunks(file[choosed_idx:])
    else:
        print("File does not exist")


def read_file(filename, force_read=False):
    """Read a PNG file"""
    reset_offset()
    if exists(filename):
        with open(filename, "rb") as fp:
            if force_read:
                file = fp.read()
            else:
                file = fp
            data = split_png_chunks(file)
        return data
    else:
        print("File does not exist")


def split_png_chunks(fp):
    if hasattr(fp, "read"):
        size = fstat(fp.fileno()).st_size
    else:
        size = len(fp)
    print(f"Reading ({size} bytes)")
    remaining_size = size
    magic_len = len(PNG_MAGIC)
    signature = read_from_file(fp, magic_len)
    remaining_size -= magic_len
    if signature != PNG_MAGIC:
        raise ValueError("File is not a PNG")
    chunks = []
    idx = 0
    while True:
        if remaining_size <= 0:
            break
        length, chunk_type, data, crc, errors = read_chunk(fp, remaining_size)
        if ERROR_CODE["EOF"] in errors:
            break
        remaining_size -= length + 4 + len(chunk_type) + len(crc)
        if ERROR_CODE["WRONG_LENGTH"] in errors:
            if len(data) > 0 and data[-4:] == b"IEND":
                chunk1 = [length, chunk_type, data[:-12], data[-12:-8], errors]
                print_chunks([chunk1], idx)
                chunks.append(chunk1)
                len_iend = int.from_bytes(data[-8:-4], byteorder="big")
                iend_errors = []
                if len_iend > 0:
                    iend_errors.append(ERROR_CODE["WRONG_LENGTH"])
                chunk2 = [len_iend, data[-4:], b"", crc, iend_errors]
                idx += 1
                print_chunks([chunk2], idx)
                chunks.append(chunk2)
        else:
            chunk_to_add = [length, chunk_type, data, crc, errors]
            print_chunks([chunk_to_add], idx)
            chunks.append(chunk_to_add)
        idx += 1
    return chunks


def write_png(chunks, output_file):
    print(f"----> Writing {output_file}")
    print_chunks(chunks)
    with open(output_file, "wb") as file:
        file.write(b"\x89PNG\r\n\x1a\n")
        for one_chunk in chunks:
            file.write(get_binary_chunk(one_chunk))


def print_chunks(chunks, start_index=0):
    if len(chunks) == 0:
        return
    max_str = max([len(f"{one_chunk[0]}") for one_chunk in chunks])
    for i, chunk in enumerate(chunks):
        crc_hex = try_hex(chunk[3])
        checksum = calculate_crc(chunk[1], chunk[2])
        is_correct = chunk[3] == checksum
        data_display = chunk[2][:5] + b"..." if len(chunk[2]) > 10 else chunk[2]
        errors = ""
        if len(chunk[4]) > 0:
            errors = f"Errors: {chunk[4]}"
        print(
            f"Chunk {start_index+i:2d}: Length={chunk[0]:{max_str}d}, Type={try_dec(chunk[1])}, CRC={crc_hex} ({is_correct}), data={data_display} {errors}"
        )


def calculate_crc(chunk_type, data):
    i = zlib.crc32(chunk_type + data) & 0xFFFFFFFF
    return i.to_bytes(4, "big")


def create_ihdr_chunk(width, height):
    chunk_type = b"IHDR"
    data = (
        width.to_bytes(4, byteorder="big")
        + height.to_bytes(4, byteorder="big")
        + b"\x08"  # 8 bits per channel
        + b"\x06"  # RGBA
        + b"\x00"  # Compression method
        + b"\x00"  # Filter method
        + b"\x00"  # Interlace method
    )
    crc = calculate_crc(chunk_type, data)
    return [len(data), chunk_type, data, crc, []]


def create_iend_chunk():
    chunk_type = b"IEND"
    data = b""
    crc = calculate_crc(chunk_type, data)
    return [len(data), chunk_type, data, crc, []]


def remove_chunk_by_type(chunks, filter_type):
    return [one_chunk for one_chunk in chunks if one_chunk[1] != filter_type]


def fix_chunk(chunk):
    chunk[0] = len(get_data_of_chunk(chunk))
    if chunk[1] not in CHUNKS_TYPES:
        chunk[1] = b"IDAT"
    chunk[3] = calculate_crc(chunk[1], get_data_of_chunk(chunk))
    chunk[4] = []
    return chunk


def get_indices(x: list, value: int) -> list:
    indices = list()
    i = 0
    while True:
        try:
            # find an occurrence of value and update i to that index
            i = x.index(value, i)
            # add i to the list
            indices.append(i)
            # advance i by 1
            i += 1
        except ValueError as _e:
            break
    return indices


def get_binary_chunk(chunk):
    length_binary = chunk[0].to_bytes(4, byteorder="big")
    type_binary = chunk[1]
    data = get_data_of_chunk(chunk)
    crc = chunk[3]
    return length_binary + type_binary + data + crc


def extract_sub_chunk(one_chunk):
    chunked = get_binary_chunk(one_chunk)
    indices = get_indices(chunked, b"IDAT")
    len_idat = len(b"IDAT")
    chunks = []
    start_chunk = indices[0]
    for i, one_indice in enumerate(indices):
        length_binary = chunked[start_chunk - 4 : start_chunk]
        real_length = int.from_bytes(length_binary, byteorder="big")
        if real_length <= 0:
            continue
        type_idat = chunked[start_chunk : start_chunk + 4]
        assert type_idat == b"IDAT"
        data_start = start_chunk + len_idat
        data = chunked[data_start : data_start + real_length]
        crc_start = data_start + real_length
        crc = chunked[crc_start : crc_start + 4]
        real_crc = calculate_crc(type_idat, data)
        if crc != real_crc:
            continue
        start_chunk = one_indice
        chunk = [
            real_length,
            type_idat,
            data,
            crc,
            [],
        ]
        chunks.append(chunk)
    return chunks


def try_decompress(data):
    try:
        return zlib.decompress(data)
    except zlib.error as e:
        print(e)
    return None


def decode_ihdr(data):
    width = int.from_bytes(data[0:4], byteorder="big")
    height = int.from_bytes(data[4:8], byteorder="big")
    bit_depth = data[8]
    color_type = data[9]
    compression_method = data[10]
    filter_method = data[11]
    interlace_method = data[12]
    return (
        width,
        height,
        bit_depth,
        color_type,
        compression_method,
        filter_method,
        interlace_method,
    )


def undo_filtering(scanline, prev_scanline=None, bpp=3):
    if prev_scanline is None:
        prev_scanline = bytes([0] * (len(scanline) - 1))

    filter_type = scanline[0]
    filtered_scanline = bytearray(scanline[1:])

    if filter_type == 0:
        return filtered_scanline
    elif filter_type == 1:
        for i in range(bpp, len(filtered_scanline)):
            filtered_scanline[i] = (
                filtered_scanline[i] + filtered_scanline[i - bpp]
            ) % 256
        return filtered_scanline
    elif filter_type == 2:
        for i in range(len(filtered_scanline)):
            filtered_scanline[i] = (filtered_scanline[i] + prev_scanline[i]) % 256
        return filtered_scanline
    elif filter_type == 3:
        for i in range(len(filtered_scanline)):
            left = filtered_scanline[i - bpp] if i >= bpp else 0
            up = prev_scanline[i]
            filtered_scanline[i] = (filtered_scanline[i] + (left + up) // 2) % 256
        return filtered_scanline
    elif filter_type == 4:
        for i in range(len(filtered_scanline)):
            left = filtered_scanline[i - bpp] if i >= bpp else 0
            up = prev_scanline[i]
            up_left = prev_scanline[i - bpp] if i >= bpp else 0
            p = left + up - up_left
            pa = abs(p - left)
            pb = abs(p - up)
            pc = abs(p - up_left)
            if pa <= pb and pa <= pc:
                pr = left
            elif pb <= pc:
                pr = up
            else:
                pr = up_left
            filtered_scanline[i] = (filtered_scanline[i] + pr) % 256
        return filtered_scanline
    else:
        raise ValueError(f"Invalid filter type: {filter_type}")


def parse_idat(idat_data, width, height, bit_depth, color_type):
    if color_type == 2:  # RGB
        bpp = 3
    elif color_type == 6:  # RGBA
        bpp = 4
    else:
        raise ValueError("Unsupported color type")

    bytes_per_pixel = (bit_depth * bpp) // 8
    scanline_length = width * bytes_per_pixel
    scanline_bytes = scanline_length + 1  # Plus 1 for the filter type byte

    bmp_data = bytearray()
    prev_scanline = None

    for i in range(height):
        scanline_start = i * scanline_bytes
        scanline_end = scanline_start + scanline_bytes
        scanline = idat_data[scanline_start:scanline_end]
        filtered_scanline = undo_filtering(scanline, prev_scanline, bytes_per_pixel)

        if color_type == 6:  # RGBA to RGB
            filtered_scanline = bytes(
                filtered_scanline[j]
                for j in range(len(filtered_scanline))
                if (j + 1) % 4 != 0
            )

        bmp_data.extend(filtered_scanline)
        prev_scanline = filtered_scanline

    return bmp_data


if __name__ == "__main__":
    print("pngtools package loaded")
