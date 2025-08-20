# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2025 Scipp contributors (https://github.com/scipp)
from pathlib import Path


def fetch_data(name: str, quiet=True) -> str:
    """
    Fetch pre-prepared data from a remote source and return the path to the folder
    containing the extracted files.

    Parameters
    ----------
    name:
        Name of the dataset to fetch. This corresponds to the name of the zip file
        without the ".zip" extension.
    quiet:
        If True, suppresses logging output. Defaults to True.
    """
    import pooch

    logger = pooch.get_logger()
    logger.setLevel("ERROR" if quiet else "INFO")

    file_path = pooch.retrieve(
        url=f"https://public.esss.dk/groups/scipp/dmsc-summer-school/2025/{name}.zip",
        known_hash=None,
        processor=pooch.Unzip(),
    )

    # With the Unzip processor, `retrieve` returns a list of files that were in the zip
    # archive.
    # If len=1, then there was only a single file, and we return the path to that file.
    # If there were more than one file, we return the path to the parent folder.
    if len(file_path) > 1:
        path = Path(file_path[0])
        return str(path.parent.absolute())
    else:
        return file_path[0]
