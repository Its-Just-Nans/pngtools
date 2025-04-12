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


def create_ppm(filename, width, height, raw_data):
    """Create a PPM file."""
    write_ascii_ppm(filename, width, height, raw_data)
