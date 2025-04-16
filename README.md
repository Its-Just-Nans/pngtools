# pngtools

Tiny CLI to explore PNG files. Supports a subset of the PNG format and acropalypse function.

[![asciicast](https://asciinema.org/a/715961.svg)](https://asciinema.org/a/715961)

## Usage

```bash
python -m pip install pngtools

# start the CLI
python -m pngtools
```

## Python usage

```python
from pngtools import PNG_MAGIC, split_png_chunks
# do your things
```

## Testing and linting

```bash
python -m pytest -vvv
python -m pylint ./pngtools
```

## License

- [MIT](LICENSE)
