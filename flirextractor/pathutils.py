import pathlib
import typing

if typing.TYPE_CHECKING:
    import os  # noqa: F401, seems to be an issue with pyflake

Path = typing.Union["os.PathLike", typing.Text]


def get_str_filepath(filepath: Path) -> str:
    """Returns the input filepath as a string.

    Raises:
        FileNotFoundError if the file cannot be found.
        IsADirectoryError if the file is a directory.
    """
    path = pathlib.Path(filepath)
    # raises FileNotFoundError if does not exist
    abs_path = path.resolve(strict=True)
    if abs_path.is_dir():
        raise IsADirectoryError(f"Give filepath '{path}' is a directory.")
    return str(abs_path)
