import pathlib
import sys

_cur_dir = pathlib.Path(__file__).resolve().parent
_scicat_tool_dir = _cur_dir.parent / "6-scicat/tools"
sys.path.append(_scicat_tool_dir.as_posix())

from scicat_widgets import upload_widget  # noqa: E402
