"""PPM file format support."""


def write_ascii_ppm(filename, width, height, raw_data):
    """Write a PPM file."""
    # Open the file and write the BMP headers and pixel data
    buffer = []
    # Write the PPM header
    buffer.append("P3\n")
    buffer.append(f"{width} {height}\n")
    buffer.append("255\n")  # Max color value
    # Write the pixel data
    for i in range(0, len(raw_data), 3):
        r = raw_data[i]
        g = raw_data[i + 1]
        b = raw_data[i + 2]
        buffer.append(f"{r} {g} {b}\n")
    buffer.append("\n")
    with open(filename, "wb") as f:
        f.write("".join(buffer).encode("utf-8"))


def write_binary_ppm(filename, width, height, raw_data):
    """Write a PPM file."""
    # Open the file and write the BMP headers and pixel data
    with open(filename, "wb") as f:
        # Write the PPM header
        f.write(b"P6\n")
        f.write(f"{width} {height}\n".encode("utf-8"))
        f.write(b"255\n")  # Max color value
        # Write the pixel data
        f.write(raw_data)


def convert_rgba_to_rgb(raw_data) -> bytearray:
    """Convert RGBA data to RGB data."""
    # RGBA to RGB - we remove the 4th value of each pixel
    return bytearray(
        raw_data[i + j] for i in range(0, len(raw_data), 4) for j in range(3)
    )


def create_ppm(filename, width, height, raw_data, binary=False):
    """Create a PPM file.

    This functions needs a RGB array of data. (RGBRGBRGB...)
    RGBA should be converted to RGB before calling this function.

    PPM can be either ASCII or binary. This function creates an ASCII PPM file.
    """
    if binary:
        write_binary_ppm(filename, width, height, raw_data)
    else:
        write_ascii_ppm(filename, width, height, raw_data)
