from pngtools import (
    read_file,
    remove_chunk_by_type,
    create_iend_chunk,
    create_bmp,
    decode_ihdr,
    extract_data,
    parse_idat,
    extract_idat,
)


def test_decode_idat():
    chunks = read_file("tests/511-200x300.png")
    assert len(chunks) == 23


def test_remove_chunk_by_type():
    chunks = read_file("tests/511-200x300.png")
    chunks = remove_chunk_by_type(chunks, b"tEXt")
    assert len(chunks) == 12


def test_delete_create_iend():
    chunks = read_file("tests/511-200x300.png")
    chunks = remove_chunk_by_type(chunks, b"IEND")
    chunks.append(create_iend_chunk())
    assert len(chunks) == 23
    assert chunks[-1][1] == b"IEND"


def test_decode_ihdr():
    chunks = read_file("tests/511-200x300.png")
    assert len(chunks) == 23
    assert chunks[0][1] == b"IHDR"
    (
        width,
        height,
        bit_depth,
        color_type,
        compression_method,
        filter_method,
        interlace_method,
    ) = decode_ihdr(chunks[0][2])
    assert width == 200
    assert height == 300
    assert bit_depth == 8
    assert color_type == 2
    assert compression_method == 0
    assert filter_method == 0
    assert interlace_method == 0


def test_convert_to_bitmap():
    chunks = read_file("tests/acropalypse.png")
    (
        width,
        height,
        bit_depth,
        color_type,
        _,
        _,
        _,
    ) = decode_ihdr(chunks[0][2])
    data = extract_idat(chunks)
    assert len(data) == 3

    data = extract_data(chunks)
    assert len(data) == 5073561
    data = parse_idat(data, width, height, bit_depth, color_type)
    create_bmp(width, height, "tests/acropalypse.bmp", data)


def test_convert_to_bitmap_classic():
    chunks = read_file("tests/511-200x300.png")
    (
        width,
        height,
        bit_depth,
        color_type,
        _,
        _,
        _,
    ) = decode_ihdr(chunks[0][2])
    from PIL import Image

    png_img = Image.open("tests/511-200x300.png")
    png_img.save("tests/511-200x300_pil.bmp")
    data = extract_data(chunks)
    assert len(data) == 200 * 300 * 3 + 300
    data = parse_idat(data, width, height, bit_depth, color_type)
    assert len(data) == 200 * 300 * 3
    create_bmp(width, height, "tests/511-200x300.bmp", data)
