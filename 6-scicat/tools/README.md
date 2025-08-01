There is a scicat widget module in this location.<br>
The widget module is developed only for the summer school, in VISA.

We will remove this tool once we package an official scicat ipywidgets.

Until then we will keep this tool with the school material.

# Loading Scicat Widget
The `tools` location should be manually added to the `sys.path`.<br>
Here is an example of scicat helper module in McStas course material:

```python
import pathlib
import sys

widget_module_path = (pathlib.Path(__file__).parent.parent / pathlib.Path('6-scicat/tools/')).resolve().as_posix()
sys.path.append(widget_module_path)

from scicat_widgets import upload_widget

```

# Debugging Configuration File

If there is a configuration file called `SCICAT_WIDGET_DEBUGGING.yml` in this location,
`scicat_widgets` module recognizes it as a debugging mode
and load the configuration to apply debugging information in the widget. <br>
(`yaml` is chosen as it allows comments, easy to read for humans and compact.)

Here is the example yaml configuration you can copy to create a file.

```yaml
token: "very-long-token-that-you-should-not-share-with-any-one"  # You can store a token here for debugging.
proposal_mount: "./notebooks/myProposals/"  # To find a proposal information and complete source folder path.
                                            # It's `/home/${USER}/myProposals/` in VISA.
proposal_id: "213256"
backend_address: "http://backend.localhost/api/v3"  # For connecting to the scicat backend.
client_address: "http://localhost" # For making a link to a new dataset in scicat web client.

# For Download Widget
download_pid: "undefined/2b85ddff-6ab6-4b46-837f-499b17e0b0ad"
target_dir: "/Users/sunyoungyoo/ESS/dmsc-school/6-scicat/notebooks/myProposals/213256/derived/"

```

# Development Log

## File Path Input
### Why text input widget instead of a file browser widget?
The file browser widget in ipywidgets is only for the local location where the browser is running.

For example, if I connect to the jupyter lab and open the file browser widget, it will show a finder on my laptop, not the VISA instance.<br>
However, if I open a jupyter lab in the virtual machine and use the browser IN the VISA, it will show the file browser of the VISA instance.

We want to use our own browser, not the one in the virtual desktop so we can't use the file browser widget to select files to upload.

However, we do want a minimum sanity check of the path so it has a wrapper widget that allows adding the path only if it exists.

## Home Directory
When you copy a path from a jupyter lab file browser, (the panel on the left)<br>
It gives you path relative to the default path (the one you see when you start the jupyter lab).

It does not give you an absolute path.

That is why there is a helper function to see if the file path is relative to the default path or not.<br>
It's called `fix_jupyter_path` in `_core_widgets.py`.

## Side Effect Confirmation/Animation
A bit chunk of code is for making a confirmation page and making an animation reaction for a button.<br>
I couldn't find a nice way of making animation than this...<br>

## Tabs
We decided to use tabs for different step of the uploading/downloading as it is natural to follow them from left to right.<br>

## For Future Refactoring
I think it's the best to separate widget building action and handler assigning action.<br>
For example, we should build the widget first and then in the higher level the handler actions should be applied.<br>
Currently a lot of handlers are created by the constructors.

## Logging

For now we use custom handler but we can later maybe just use rich handelr.
I have used it for debugging but now it's removed.

```python
from rich.logging import RichHandler

handler = RichHandler()
logger.addHandler(handler)
```
