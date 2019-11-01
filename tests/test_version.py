import tomlkit

import flirextractor


def test_version():
    with open("./pyproject.toml", "r") as tomlfile:
        contents = tomlfile.read()
        parsed_contents = tomlkit.parse(contents)
    loaded_version = parsed_contents["tool"]["poetry"]["version"]
    assert flirextractor.__version__ == loaded_version
