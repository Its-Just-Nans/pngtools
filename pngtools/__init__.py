"""main module"""

from .lib import (
    split_png_chunks,  # noqa: F401
    write_png,  # noqa: F401
    print_chunks,  # noqa: F401
    fix_chunk,  # noqa: F401
    create_ihdr_chunk,  # noqa: F401
    remove_chunk_by_type,  # noqa: F401
    create_iend_chunk,  # noqa: F401
    extract_sub_chunk,  # noqa: F401
    try_decompress,  # noqa: F401
    read_file,  # noqa: F401
    decode_ihdr,  # noqa: F401
    extract_data,  # noqa: F401
    parse_idat,  # noqa: F401
    extract_idat,  # noqa: F401
    read_broken_file,  # noqa: F401
)

from .bmp import create_bmp  # noqa: F401
from .cli import (
    cli_main,  # noqa: F401
    CLI,  # noqa: F401
)
