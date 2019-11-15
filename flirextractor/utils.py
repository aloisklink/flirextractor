"""Stores utilility functions that don't go anywhere else.
"""
import typing

V = typing.TypeVar("V")


def split_dict(
    input_dict: typing.Mapping[str, V], include: typing.Iterable[str],
) -> typing.Tuple[typing.Dict[str, V], typing.Dict[str, V]]:
    """Splits a dict into two by key

    Parameters:
        input_dict: The dict to split
        include: The keys to put into the include dict

    Returns:
        `included, excluded`:
        A dict with the included keys, and a dict with the excluded keys
    """
    excluded_dict = dict(**input_dict)  # so we don't modify original
    included_dict = {
        key: excluded_dict.pop(key)  # remove from excluded dict
        for key in include
        if key in excluded_dict
    }
    return included_dict, excluded_dict
