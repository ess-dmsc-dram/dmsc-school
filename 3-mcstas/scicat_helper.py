import os
import pathlib
import sys

widget_module_path = (
    pathlib.Path(__file__).parent.parent
    .joinpath("6-scicat", "tools")
    .resolve()
)
sys.path.append(os.fspath(widget_module_path))

from scicat_widgets import upload_widget

__all__ = ["upload_widget"]
