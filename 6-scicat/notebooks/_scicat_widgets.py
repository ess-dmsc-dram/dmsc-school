import pathlib

from typing import Any
from functools import partial
from ipywidgets import widgets
from ipywidgets import Layout
from IPython.display import display

default_layout = Layout(width="auto")
default_style = {"description_width": "auto"}


def import_pyperclip():
    try:
        import pyperclip
    except ImportError as e:
        raise ImportError(
            "pyperclip is not installed. Please install it to use the copy/paste functionality."
            "It is because ipywidget panel cannot access to the clipboard in some platforms."
            " See https://github.com/microsoft/vscode-jupyter/issues/15787#issuecomment-2918592937 for more details."
            "Therefore there is a button to copy/paste from clipboard."
            "Note that these buttons are extra feature and are not required to all platforms."
        ) from e
    # TODO: Check how to display this error in the widget
    return pyperclip


def paste_from_clipboard(_: Any, *, token_widget: widgets.ValueWidget) -> None:
    """
    Paste the SciCat token from the clipboard into the token text box.
    """
    pyperclip = import_pyperclip()
    token_widget.value = pyperclip.paste()


def copy_to_clipboard(_: Any, *, token_widget: widgets.ValueWidget) -> None:
    """
    Paste the SciCat token from the clipboard into the token text box.
    """
    pyperclip = import_pyperclip()
    pyperclip.copy(token_widget.value)


class NotSoLongButNotShortText(widgets.HBox):
    def __init__(
        self, *args, entry_widget: type[widgets.Widget] = widgets.Text, **kwargs: Any
    ):
        self.text = entry_widget(*args, **kwargs)
        self.paste_button = widgets.Button(
            description="Paste",
            tooltip="Paste from clipboard",
            layout=Layout(width="80px"),
            style=default_style,
        )
        self.copy_button = widgets.Button(
            description="Copy",
            tooltip="Copy to clipboard",
            layout=Layout(width="80px"),
            style=default_style,
        )

        self.paste_button.on_click(
            partial(paste_from_clipboard, token_widget=self.text)
        )
        self.copy_button.on_click(partial(copy_to_clipboard, token_widget=self.text))

        super().__init__(
            children=[self.text, self.paste_button, self.copy_button],
            layout=default_layout,
            style=default_style,
        )

    @property
    def value(self) -> str:
        return self.text.value

    @value.setter
    def value(self, new_value: str) -> None:
        self.text.value = new_value

    @property
    def disabled(self) -> bool:
        """
        Get the enabled state of the text box.
        """
        return self.text.disabled

    @disabled.setter
    def disabled(self, new_value: bool) -> None:
        """
        Set the enabled state of the text box.
        If new_value is True, the text box is enabled; otherwise, it is disabled.
        """
        self.text.disabled = new_value

    def __str__(self) -> str:
        return self.text


_DEBUGGING_FILE_PATH = pathlib.Path("./SCICAT_WIDGET_DEBUGGING")


def _is_debugging() -> bool:
    """
    Check if the debugging file exists.
    This is used to determine if the widget should use a default address and token.
    """

    return _DEBUGGING_FILE_PATH.exists()


def _get_default_address() -> str:
    """
    Get the default address and token for the SciCat widget.
    If debugging is enabled, it reads from a file; otherwise, it uses a staging address.
    """
    if _is_debugging():
        import json

        data = json.loads(_DEBUGGING_FILE_PATH.read_text())
        return data.get("address", "http://backend.localhost/api/v3")
    else:
        return "https://staging.scicat.ess.eu/api/v3"


def _get_default_token() -> str:
    """
    Get the default address and token for the SciCat widget.
    If debugging is enabled, it reads from a file; otherwise, it uses a staging address.
    """
    if _is_debugging():
        import json

        data = json.loads(_DEBUGGING_FILE_PATH.read_text())
        return data.get("token", "")
    else:
        return ""


class AddressBox(widgets.HBox):
    def __init__(self):
        default_address = _get_default_address()
        self.checkbox = widgets.Checkbox(
            value=False,
            description="Enable Editing",
            layout=Layout(width="20%"),
            style=default_style,
        )
        layout = Layout(width="80%", min_width="300px")
        self.address = NotSoLongButNotShortText(
            default_address,
            description="Scicat Address",
            layout=layout,
            style=default_style,
            disabled=True,  # Disable editing the address
        )

        def toggle_editing(_: Any) -> None:
            """
            Toggle the enabled state of the address text box based on the checkbox.
            If the checkbox is checked, the address text box is enabled; otherwise, it is disabled.
            """
            self.address.disabled = not self.checkbox.value

        self.checkbox.observe(toggle_editing, names="value")
        super().__init__(
            children=[
                self.address,
                self.checkbox,
            ],
            layout=default_layout,
            style=default_style,
        )

    @property
    def value(self) -> str:
        """
        Get the current value of the address.
        If the checkbox is checked, it returns the address; otherwise, it returns an empty string.
        """
        return self.address.value


class CredentialBox(widgets.VBox):
    def __init__(self):
        default_token = _get_default_token()

        self.address_box = AddressBox()
        self.token = NotSoLongButNotShortText(
            value=default_token,
            placeholder="Enter token copied from SciCat",
            description="Scicat Token",
        )
        super().__init__(
            children=[self.address_box, self.token],
            titles=["Credentials"],
            layout=default_layout,
            style=default_style,
        )


class DownloadBox(widgets.VBox):
    def __init__(
        self, credential_box: CredentialBox, output_widget: widgets.Output, **kwargs
    ):
        self.output = output_widget
        self.credential_box = credential_box
        self.pid_entry = widgets.Textarea(
            description="PID",
            placeholder="Enter the PID of the dataset to download.\n"
            "Separate multiple PIDs with space or newlines.\n"
            "Click 'Add' to add them to the download list below.",
            layout=Layout(width="80%"),
            style=default_style,
        )
        self.add_button = widgets.Button(
            description="Add",
            tooltip="Add the PID to the download list",
            layout=Layout(width="20%"),
            style=default_style,
        )
        pid_entry_box = widgets.HBox(
            children=[self.pid_entry, self.add_button],
            layout=Layout(width="100%"),
            style=default_style,
        )

        def add_action(_) -> None:
            """
            Action to perform when the 'Add' button is clicked.
            It should add the PID from the entry box to the download list.
            """
            pids = []
            pids_text = self.pid_entry.value.strip()
            for pid_line in pids_text.splitlines():
                pid_line = pid_line.strip()
                if pid_line:
                    pids.extend(pid_line.split())

            if pids:
                with output_widget:
                    print(f"Adding PIDs to download list: {', '.join(pids)}")

                for pid in pids:
                    self._add_download_target(pid)

            self.pid_entry.value = ""

        self.add_button.on_click(add_action)
        super().__init__([pid_entry_box], **kwargs)

    def _add_download_target(self, pid: str) -> None:
        label = widgets.Label(
            value=pid, layout=Layout(width="80%", align_self="center")
        )
        download_button = widgets.Button(
            description="💾",
            tooltip=f"Download dataset with PID {pid}",
            layout=Layout(width="auto"),
            style=default_style,
        )
        delete_button = widgets.Button(
            description="❌",
            tooltip=f"Remove dataset with PID {pid} from download list",
            layout=Layout(width="auto"),
            style=default_style,
        )

        download_target_widget = widgets.HBox([delete_button, download_button, label])

        def _delete_action(_) -> None:
            """
            Action to perform when the 'Delete' button is clicked.
            It should remove the download target from the list.
            """
            with self.output:
                print(f"Removing PID {pid} from download list")

            self.children = tuple(
                child for child in self.children if child is not download_target_widget
            )

        delete_button.on_click(_delete_action)
        self.children = (*self.children, download_target_widget)


class ScicatWidget(widgets.VBox):
    def __init__(
        self,
        *,
        credential_box: CredentialBox,
        output_widget: widgets.Output,
        download_widget: DownloadBox | None = None,
        upload_widget=None,
        download_registry: dict | None = None,
    ):
        self.download_registry = download_registry or {}
        self.upload_widget = upload_widget
        self.download_widget = download_widget
        self.credentials = credential_box

        self._sub_widgets = {
            "Credentials": self.credentials,
            "Upload": self.upload_widget,
            "Download": self.download_widget,
        }

        self.tabs = {
            name: widget
            for name, widget in self._sub_widgets.items()
            if widget is not None  # Only include non-None widgets
        }
        self.menus = widgets.Accordion(
            children=list(self.tabs.values()),
            titles=tuple(self.tabs.keys()),
            layout=Layout(height="auto"),
            style=default_style,
        )
        self.menus.selected_index = 1 if _is_debugging() else 0

        self.output = output_widget
        with self.output:
            print(
                "Welcome to the SciCat widget! "
                "Please enter your SciCat credentials in the Credentials tab."
            )
        output_box = widgets.Accordion(children=[self.output], titles=["Output (Log)"])
        output_box.selected_index = 0

        super().__init__(
            children=[
                widgets.HTML("<h2>Scicat Widget</h2>"),
                widgets.VBox([self.menus, output_box]),
            ],
            layout=default_layout,
            style=default_style,
        )


def download_widget(
    download_registry: dict | None = None, show: bool = True
) -> ScicatWidget:
    download_registry = download_registry or {}
    credential_box = CredentialBox()
    output = widgets.Output(
        layout=Layout(
            overflow="scroll hidden",
            flex_flow="row",
            width="auto",
            display="flex",
            height="auto",
            marging="10px",
            padding="10px",
        ),
        style=default_style,
    )
    output.layout.border = "1px solid black"
    widget = ScicatWidget(
        credential_box=credential_box,
        output_widget=output,
        download_widget=DownloadBox(
            credential_box=credential_box, output_widget=output
        ),
        download_registry=download_registry,
    )
    if show:
        display(widget)
    return widget


def scicat_widget(download_registry: dict | None = None) -> widgets.Widget:
    return ScicatWidget()


def validate_token(token: str) -> bool:
    # Try connecting to the SciCat API with the provided token.
    from scitacean.util.credentials import ExpiringToken

    token_obj = ExpiringToken.from_jwt(token)
    try:
        token_obj.get_str()
    except Exception as e:
        print(f"Invalid token: {e}")
        return False
