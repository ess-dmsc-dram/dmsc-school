# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2025 Scipp contributors (https://github.com/scipp)


def fetch_data(name: str) -> str:
    """
    Fetch pre-prepared data from a remote source and return the path to the folder
    containing the extracted files.
    """
    import pooch
    from pathlib import Path

    file_path = pooch.retrieve(
        url=f"https://public.esss.dk/groups/scipp/dmsc-summer-school/2025/{name}.zip",
        known_hash=None,
        processor=pooch.Unzip(),
    )

    path = Path(file_path[0])
    return str(path.parent.absolute())
