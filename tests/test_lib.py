"""Unit tests for pngtools library."""

from os.path import getsize
import filecmp
from PIL import Image  # python -m pip install pillow

from pngtools import (
    read_file,
    read_broken_file,
    remove_chunk_by_type,
    create_iend_chunk,
    create_bmp,
    create_ppm,
    decode_ihdr,
    extract_data,
    parse_idat,
    extract_idat,
    get_by_type,
    get_data_of_chunk,
    get_type_of_chunk,
    get_length_of_chunk,
    calculate_decompressed_length,
    decode_phy,
)


def test_read_file():
    """Test reading a PNG file."""
    chunks = read_file("tests/511-200x300.png")
    assert len(chunks) == 23


def test_force_read():
    """Test reading a PNG file with force_read=True."""
    chunks = read_file("tests/511-200x300.png", force_read=True)
    assert len(chunks) == 23


def test_decode_broken_file():
    """Test reading a broken PNG file."""
    chunks, _ = read_broken_file("tests/broken_file.bin")
    assert len(chunks) == 23


def test_decode_broken_file_multiple():
    """Test reading a broken PNG file with multiple chunks."""
    filename = "tests/double_png.png"
    chunks_file_0, idxs = read_broken_file(filename)
    assert len(chunks_file_0) == 23 + 2  # 2 = chunk raw data + detected IEND

    # force idxs[1] to be chosen
    idx_chosen = idxs[1]
    chunks_file_1, _ = read_broken_file(filename, force_idx=idx_chosen)
    assert len(chunks_file_1) == 23


def test_remove_chunk_by_type():
    """Test removing a chunk by type."""
    chunks = read_file("tests/511-200x300.png")
    chunks = remove_chunk_by_type(chunks, b"tEXt")
    assert len(chunks) == 12


def test_delete_create_iend():
    """Test deleting and creating an IEND chunk."""
    chunks = read_file("tests/511-200x300.png")
    chunks = remove_chunk_by_type(chunks, b"IEND")
    chunks.append(create_iend_chunk())
    assert len(chunks) == 23
    assert chunks[-1][1] == b"IEND"


def test_decode_ihdr():
    """Test decoding the IHDR chunk."""
    chunks = read_file("tests/511-200x300.png")
    assert len(chunks) == 23
    assert get_type_of_chunk(chunks[0]) == b"IHDR"
    (
        width,
        height,
        bit_depth,
        color_type,
        compression_method,
        filter_method,
        interlace_method,
    ) = decode_ihdr(get_data_of_chunk(chunks[0]))
    assert width == 200
    assert height == 300
    assert bit_depth == 8
    assert color_type == 2
    assert compression_method == 0
    assert filter_method == 0
    assert interlace_method == 0


def test_decode_phy():
    """Test decoding the pHYs chunk."""
    chunks = read_file("tests/511-200x300.png")
    phy = get_by_type(chunks, b"pHYs")[0]
    x, y, unit = decode_phy(phy)
    assert x == 2834
    assert y == 2834
    assert unit == 1


def test_acropalypse_to_bitmap():
    """Convert PNG to BMP format."""
    chunks = read_file("tests/acropalypse.png")
    (
        width,
        height,
        bit_depth,
        color_type,
        _,
        _,
        _,
    ) = decode_ihdr(get_data_of_chunk(chunks[0]))
    data = extract_idat(chunks)
    assert len(data) == 3

    total_length = sum(
        [get_length_of_chunk(one_chunk) for one_chunk in get_by_type(chunks, b"IDAT")]
    )

    assert len(b"".join(data)) == total_length

    data = extract_data(chunks)
    expected_length = calculate_decompressed_length(
        width, height, bit_depth, color_type
    )
    assert len(data) == expected_length

    raw_data = parse_idat(data, width, height, bit_depth, color_type)
    # Determine the number of color and alpha planes
    alpha_planes = 1 if color_type & 4 else 0  # Alpha channel
    color_planes = 3 if color_type & 2 else 1  # RGB or grayscale

    # Total planes (color + alpha)
    planes = color_planes + alpha_planes

    # Adjust the assertion based on bit depth and number of planes
    expected_size = width * height * planes * (bit_depth // 8)
    assert len(raw_data) == expected_size, (
        f"Expected {expected_size}, but got {len(raw_data)}"
    )
    create_bmp(
        "tests/acropalypse.bmp",
        width,
        height,
        bit_depth,
        color_type,
        raw_data,
    )


def test_convert_to_bitmap():
    """Convert PNG to BMP format."""
    chunks = read_file("tests/511-200x300.png")
    (
        width,
        height,
        bit_depth,
        color_type,
        _,
        _,
        _,
    ) = decode_ihdr(get_data_of_chunk(chunks[0]))
    data = extract_data(chunks)
    assert len(data) == calculate_decompressed_length(
        width, height, bit_depth, color_type
    )
    raw_data = parse_idat(data, width, height, bit_depth, color_type)
    # Determine the number of color and alpha planes
    alpha_planes = 1 if color_type & 4 else 0  # Alpha channel
    color_planes = 3 if color_type & 2 else 1  # RGB or grayscale

    # Total planes (color + alpha)
    planes = color_planes + alpha_planes

    # Adjust the assertion based on bit depth and number of planes
    expected_size = width * height * planes * (bit_depth // 8)
    assert len(raw_data) == expected_size, (
        f"Expected {expected_size}, but got {len(raw_data)}"
    )
    create_bmp(
        "tests/511-200x300.bmp",
        width,
        height,
        bit_depth,
        color_type,
        raw_data,
    )
    _test_pil()


def _test_pil():
    png_img = Image.open("tests/511-200x300.png")
    png_img.save("tests/511-200x300_pil.bmp")
    png_img.close()

    assert getsize("tests/511-200x300_pil.bmp") == getsize("tests/511-200x300.bmp")

    assert filecmp.cmp(
        "tests/511-200x300_pil.bmp", "tests/511-200x300.bmp", shallow=False
    )


def test_convert_to_ppm():
    """Convert PNG to PPM format."""
    chunks = read_file("tests/511-200x300.png")
    (
        width,
        height,
        bit_depth,
        color_type,
        _,
        _,
        _,
    ) = decode_ihdr(get_data_of_chunk(chunks[0]))
    data = extract_data(chunks)
    assert len(data) == calculate_decompressed_length(
        width, height, bit_depth, color_type
    )
    raw_data = parse_idat(data, width, height, bit_depth, color_type)

    create_ppm(
        "tests/511-200x300.ppm",
        width,
        height,
        raw_data,
    )
