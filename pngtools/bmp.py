def png_to_bmp_data(width, height, bit_depth, color_type, raw_data):
    """Convert parsed PNG raw data to BMP pixel data."""
    # Determine number of color and alpha planes
    alpha_planes = 1 if color_type & 4 else 0  # Alpha channel
    color_planes = 3 if color_type & 2 else 1  # RGB or grayscale

    planes = color_planes + alpha_planes
    bytes_per_pixel = (bit_depth // 8) * planes
    row_size = width * bytes_per_pixel
    padded_row_size = (row_size + 3) & ~3  # BMP rows must be multiple of 4 bytes
    bmp_data = bytearray()

    for y in range(height - 1, -1, -1):  # BMP stores rows bottom to top
        row_start = y * row_size
        row = raw_data[row_start : row_start + row_size]

        if color_planes == 3:  # RGB to BGR conversion
            for x in range(0, len(row), bytes_per_pixel):
                # Convert RGB to BGR
                bmp_data.extend([row[x + 2], row[x + 1], row[x]])  # BGR format
                if alpha_planes:
                    bmp_data.append(row[x + 3])  # Append alpha if present
        elif color_planes == 1:  # Grayscale
            for x in range(0, len(row), bytes_per_pixel):
                # Grayscale value (single channel)
                bmp_data.extend(
                    [row[x]] * 3
                )  # Convert to BGR by repeating the gray value

        # Add padding to the row if necessary
        bmp_data.extend([0] * (padded_row_size - row_size))

    return bmp_data


def write_bmp(filename, width, height, bit_depth, planes, pixel_data):
    """Write the BMP file with headers and pixel data."""
    file_size = 14 + 40 + len(pixel_data)  # BMP file header + DIB header + pixel data
    bmp_file_header = bytearray(
        [
            0x42,
            0x4D,  # Signature "BM"
            file_size & 0xFF,
            (file_size >> 8) & 0xFF,
            (file_size >> 16) & 0xFF,
            (file_size >> 24) & 0xFF,  # File size
            0x00,
            0x00,  # Reserved
            0x00,
            0x00,  # Reserved
            0x36,
            0x00,
            0x00,
            0x00,  # Data offset (54 bytes)
        ]
    )

    # DIB Header (40 bytes)
    dib_header = bytearray(
        [
            0x28,
            0x00,
            0x00,
            0x00,  # DIB header size
            width & 0xFF,
            (width >> 8) & 0xFF,
            (width >> 16) & 0xFF,
            (width >> 24) & 0xFF,  # Image width
            height & 0xFF,
            (height >> 8) & 0xFF,
            (height >> 16) & 0xFF,
            (height >> 24) & 0xFF,  # Image height
            0x01,
            0x00,  # Number of color planes (must be 1)
            (bit_depth * planes) & 0xFF,
            0x00,  # Bits per pixel
            0x00,
            0x00,
            0x00,
            0x00,  # Compression (0 = None)
            len(pixel_data) & 0xFF,
            (len(pixel_data) >> 8) & 0xFF,
            (len(pixel_data) >> 16) & 0xFF,
            (len(pixel_data) >> 24) & 0xFF,  # Image size
            0xC4,
            0x0E,
            0x00,
            0x00,  # Horizontal resolution
            0xC4,
            0x0E,
            0x00,
            0x00,  # Vertical resolution
            0x00,
            0x00,
            0x00,
            0x00,  # Number of colors in palette (0 = default)
            0x00,
            0x00,
            0x00,
            0x00,  # Important colors (0 = all)
        ]
    )

    # Open the file and write the BMP headers and pixel data
    with open(filename, "wb") as f:
        f.write(bmp_file_header)
        f.write(dib_header)
        f.write(pixel_data)


def create_bmp(filename, width, height, bit_depth, color_type, raw_data):
    """Create a BMP file from PNG parameters."""
    # Determine the number of color and alpha planes
    alpha_planes = 1 if color_type & 4 else 0  # Alpha channel
    color_planes = 3 if color_type & 2 else 1  # RGB or grayscale

    # Total planes (color + alpha)
    planes = color_planes + alpha_planes

    bmp_pixel_data = png_to_bmp_data(width, height, bit_depth, color_type, raw_data)
    write_bmp(filename, width, height, bit_depth, planes, bmp_pixel_data)
