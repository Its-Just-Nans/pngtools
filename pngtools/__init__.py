from os.path import getsize

ERROR_CODE = {
    "WRONG_LENGTH": "Wrong length",
    "EOF": "End of file",
    "WRONG_CRC": "Wrong CRC",
}

CHUNKS_TYPES = {
    b"IHDR": "Image header",
    b"PLTE": "Palette",
    b"IDAT": "Image data",
    b"IEND": "Image trailer",
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


def read_chunk(file, total_size):
    readed = file.read(4)
    errors = []
    if readed == "":
        errors.append(ERROR_CODE["EOF"])
        return None, None, None, None, errors
    data_length = int.from_bytes(readed, byteorder="big")
    to_read = data_length
    if data_length > total_size:
        to_read = total_size - 3 * 4
        errors.append(ERROR_CODE["WRONG_LENGTH"])
    chunk_type = file.read(4)
    data = file.read(to_read)
    crc = file.read(4)
    if crc != calculate_crc(chunk_type, data):
        errors.append(ERROR_CODE["WRONG_CRC"])
    return data_length, chunk_type, data, crc, errors


def try_dec(a):
    try:
        return a.decode("ascii")
    except UnicodeDecodeError:
        return "????"


def try_hex(a):
    try:
        return a.hex()
    except UnicodeDecodeError:
        return "????"


def split_png_chunks(png_file):
    size = getsize(png_file)
    print(f"Reading {png_file} ({size} bytes)")
    remaining_size = size
    with open(png_file, "rb") as file:
        # PNG files start with a signature
        signature = file.read(8)
        remaining_size -= 8
        if signature != PNG_MAGIC:
            raise ValueError("File is not a PNG")

        chunks = []
        idx = 0
        while True:
            if remaining_size <= 0:
                break
            length, chunk_type, data, crc, errors = read_chunk(file, remaining_size)
            if ERROR_CODE["EOF"] in errors:
                break
            remaining_size -= length + 3 * 4
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
    for i, chunk in enumerate(chunks):
        crc_hex = try_hex(chunk[3])
        checksum = calculate_crc(chunk[1], chunk[2])
        is_correct = chunk[3] == checksum
        data_display = chunk[2][:10] + b"..." if len(chunk[2]) > 10 else chunk[2]
        print(
            f"Chunk {start_index+i}: Length={chunk[0]}, Type={try_dec(chunk[1])}, CRC={crc_hex} ({is_correct}), data={data_display} errors={chunk[4]}"
        )


def calculate_crc(chunk_type, data):
    import zlib

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
    chunk[0] = len(chunk[2])
    if chunk[1] not in CHUNKS_TYPES:
        chunk[1] = b"IDAT"
    chunk[3] = calculate_crc(chunk[1], chunk[2])
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
        except ValueError as e:
            break
    return indices


def get_binary_chunk(chunk):
    length_binary = chunk[0].to_bytes(4, byteorder="big")
    type_binary = chunk[1]
    data = chunk[2]
    crc = chunk[3]
    return length_binary + type_binary + data + crc


def extract_sub_chunk(one_chunk):
    chunked = get_binary_chunk(one_chunk)
    indices = get_indices(chunked, b"IDAT")
    chunks = []
    start_chunk = indices[0]
    for i, one_indice in enumerate(indices):
        if i == len(indices) - 1:
            next_end = len(chunked)
        else:
            next_end = indices[i + 1]
        length_binary = chunked[start_chunk - 4 : start_chunk]
        type_idat = chunked[start_chunk : start_chunk + 4]
        data = chunked[start_chunk + 4 : next_end - 4]
        crc = chunked[next_end - 4 : next_end]
        real_crc = calculate_crc(type_idat, data)
        if crc != real_crc:
            print(f"{crc} != {real_crc}")
            continue
        start_chunk = one_indice
        chunk = [
            int.from_bytes(length_binary, byteorder="big"),
            type_idat,
            data,
            crc,
            [],
        ]
        chunks.append(chunk)
    return chunks


if __name__ == "__main__":
    print("pngtools package loaded")
