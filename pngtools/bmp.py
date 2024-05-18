"""a tiny bmp utility"""


def create_bmp(width, height, filename, image_data, phy=None):
    """Create BMP"""
    if phy is None:
        x_pixels_per_meter = 2835
        y_pixels_per_meter = 2835
    else:
        x_pixels_per_meter = phy[0]
        y_pixels_per_meter = phy[1]
    # Bitmap file header (14 bytes)
    bmp_data = bytearray()
    bmp_data.extend(b"BM")  # Signature
    size = 14 + 40 + height * ((width * 3 + 3) & ~3)
    size = size.to_bytes(4, byteorder="little")
    bmp_data.extend(size)  # File size
    bmp_data.extend(b"\x00\x00\x00\x00")  # Reserved
    bmp_data.extend((14 + 40).to_bytes(4, byteorder="little"))  # Data offset

    # Bitmap information header (40 bytes)
    bmp_data.extend(b"\x28\x00\x00\x00")  # Header size
    bmp_data.extend(width.to_bytes(4, byteorder="little"))  # Image width
    bmp_data.extend(height.to_bytes(4, byteorder="little"))  # Image height
    bmp_data.extend(b"\x01\x00")  # Planes
    bmp_data.extend(b"\x18\x00")  # Bits per pixel (24-bit)
    bmp_data.extend(b"\x00\x00\x00\x00")  # Compression (none)
    bmp_data.extend(
        (height * ((width * 3 + 3) & ~3)).to_bytes(4, byteorder="little")
    )  # Image size
    bmp_data.extend(
        x_pixels_per_meter.to_bytes(4, byteorder="little")
    )  # X pixels per meter (2835)
    bmp_data.extend(
        y_pixels_per_meter.to_bytes(4, byteorder="little")
    )  # Y pixels per meter (2835)
    bmp_data.extend(b"\x00\x00\x00\x00")  # Number of colors used
    bmp_data.extend(b"\x00\x00\x00\x00")  # Number of important colors

    with open(filename, "wb") as f:
        f.write(bmp_data)
        row_size = (width * 3 + 3) & ~3
        for y in range(height - 1, -1, -1):
            row_start = y * width * 3
            row_end = row_start + width * 3
            row_data = image_data[row_start:row_end]
            bgr_data = bytearray()
            for i in range(0, len(row_data), 3):
                r = row_data[i]
                g = row_data[i + 1]
                b = row_data[i + 2]
                bgr_data.extend([b, g, r])
            f.write(bgr_data)
            f.write(b"\x00" * (row_size - len(bgr_data)))  # Add padding
