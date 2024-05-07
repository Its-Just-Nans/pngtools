"""a tiny bmp utility"""


def create_bmp(width, height, filename, image_data):
    """Create BMP"""

    # Write image data to a file

    # Bitmap file header (14 bytes)
    bmp_data = bytearray()
    bmp_data.extend(b"BM")  # Signature
    bmp_data.extend(len(image_data).to_bytes(4, byteorder="little"))  # File size
    bmp_data.extend(b"\x00\x00\x00\x00")  # Reserved
    bmp_data.extend((14 + 40).to_bytes(4, byteorder="little"))  # Data offset

    # Bitmap information header (40 bytes)
    bmp_data.extend(b"\x28\x00\x00\x00")  # Header size
    bmp_data.extend(width.to_bytes(4, byteorder="little"))  # Image width
    bmp_data.extend(height.to_bytes(4, byteorder="little"))  # Image height
    bmp_data.extend(b"\x01\x00")  # Planes
    bmp_data.extend(b"\x20\x00")  # Bits per pixel (24-bit)
    bmp_data.extend(b"\x00\x00\x00\x00")  # Compression (none)
    bmp_data.extend((len(image_data)).to_bytes(4, byteorder="little"))  # Image size
    bmp_data.extend(b"\xc4\x0e\x00\x00")  # X pixels per meter
    bmp_data.extend(b"\xc4\x0e\x00\x00")  # Y pixels per meter
    bmp_data.extend(b"\x00\x00\x00\x00")  # Number of colors used
    bmp_data.extend(b"\x00\x00\x00\x00")  # Number of important colors

    with open(filename, "wb") as f:
        f.write(bmp_data)
        f.write(image_data)
