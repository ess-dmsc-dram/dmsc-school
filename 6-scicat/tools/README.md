# SciCat Widget

This module provides a Jupyter widget for uploading datasets to SciCat based on https://github.com/SciCatProject/scicat_widget.

## Loading the Scicat Widget
The `tools` location should be manually added to the `sys.path`.
Here is an example of a scicat helper module in the McStas course material:

```python
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
```

## Testing
For testing, you can pass a custom Scitacean client to the widget instead of connecting to the actual backend.
For example:
```python
from scitacean.testing.client import FakeClient
from scitacean.testing.transfer import FakeFileTransfer

transfer = FakeFileTransfer()
client = FakeClient.without_login("staging.ess", file_transfer=transfer)

upload_widget(client=client)
```

After uploading datasets and files, you can inspect `client` and `transfer` to see what was uploaded.
Note that this does not download initial data from SciCat.
