import pathlib
import logging
from typing import Any
from functools import partial
from collections.abc import Callable
from scitacean import Client

from ipywidgets import widgets, Layout

default_layout = Layout(width="auto", min_width="560px")
default_style = {"description_width": "150px"}
button_layout = Layout(width="100%", height="36px", margin="5px")


def fix_jupyter_path(path: str) -> pathlib.Path:
    """Fix the path to be absolute if it is not.

    When you copy path from a Jupyter lab
    it is relative to the current working directory,
    which is the home directory in VISA.
    """
    original_path = pathlib.Path(path)
    if (
        not original_path.exists()
        and (from_home := pathlib.Path.home() / original_path).exists()
    ):
        return from_home
    return original_path


# Debugging configuration and default values
_DEBUGGING_FILE_PATH = pathlib.Path(__file__).parent / pathlib.Path(
    "SCICAT_WIDGET_DEBUGGING.yml"
)


def is_debugging() -> bool:
    return _DEBUGGING_FILE_PATH.exists()


def _get_debug_config() -> dict:
    """Get debugging configuration or defaults."""
    if is_debugging():
        import yaml

        return yaml.safe_load(_DEBUGGING_FILE_PATH.read_text())
    return {}


def get_default_backend_address() -> str:
    config = _get_debug_config()
    return config.get(
        "backend_address",
        "https://staging.scicat.ess.eu/api/v3"
        if not is_debugging()
        else "http://backend.localhost/api/v3",
    )


def get_default_client_address() -> str:
    config = _get_debug_config()
    return config.get(
        "client_address",
        "https://staging.scicat.ess.eu" if not is_debugging() else "http://localhost",
    )


def get_default_token() -> str:
    return _get_debug_config().get("token", "")


def _get_default_proposal_mount() -> pathlib.Path:
    if is_debugging():
        # If debugging, use the path from the debugging file
        config = _get_debug_config()
        return pathlib.Path(config.get("proposal_mount", "./myProposals/"))
    elif (symlink_path := pathlib.Path.home() / "myProposals").exists():
        return symlink_path.resolve()
    else:
        hardcoded_path = pathlib.Path("/ess/data/workshop/")
        return hardcoded_path.resolve()


def get_current_proposal() -> str:
    # The original idea was to list `~/myProposals` and return the first one.
    # However, it was not there when I logged in to the VISA with a non-ess user ID.
    # So we are hardcoding the proposal ID for the summer school.
    if is_debugging():
        # If debugging, use the proposal ID from the debugging file
        config = _get_debug_config()
        return config.get("proposal_id", "909047")
    return "909047"


def get_default_source_folder_parent() -> pathlib.Path:
    proposal_id = get_current_proposal()
    default_source_folder = pathlib.Path(
        _get_default_proposal_mount() / proposal_id / "upload"
    )
    if not default_source_folder.exists():
        import os

        return pathlib.Path(
            os.getcwd()
        ).resolve()  # Fallback to current working directory if the path does not exist
    return default_source_folder.resolve()


def get_default_download_pid() -> str:
    """Get the default PID for downloads."""
    config = _get_debug_config()
    return config.get("download_pid", "")


def get_default_target_dir() -> str:
    """Get the default target directory for downloads."""
    config = _get_debug_config()
    return config.get("target_dir", "")


# Widgets and Handlers


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
        try:
            self.paste_button = widgets.Button(
                description="Paste",
                tooltip="Paste from clipboard",
                layout=Layout(width="80px"),
            )
            self.copy_button = widgets.Button(
                description="Copy",
                tooltip="Copy to clipboard",
                layout=Layout(width="80px"),
            )

            self.paste_button.on_click(
                partial(paste_from_clipboard, token_widget=self.text)
            )
            self.copy_button.on_click(
                partial(copy_to_clipboard, token_widget=self.text)
            )

            super().__init__(
                children=[self.text, self.paste_button, self.copy_button],
                layout=default_layout,
                style=default_style,
            )
        except ImportError as e:
            # If pyperclip is not installed, just create a text widget
            get_logger().warning(e)
            super().__init__(
                children=[self.text],
                layout=Layout(width="100%", border="1px solid black"),
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
        return self.text.disabled

    @disabled.setter
    def disabled(self, new_value: bool) -> None:
        self.text.disabled = new_value

    def __str__(self) -> str:
        return self.text


def _strip_and_shorten(val_str: str, max_value_length: int = 30) -> str:
    """Strip whitespace and shorten the string if it exceeds a certain length."""
    val_str = val_str.strip()
    if len(val_str) > max_value_length - 3:
        return val_str[: max_value_length - 3] + "..."
    return val_str


def _make_svg_label(val_str: str, *, svg_height: int = 36) -> widgets.HTML:
    val_str = _strip_and_shorten(val_str)
    svg_width = (len(val_str) * 8) + 10
    return widgets.HTML(
        value=f"""<svg width="{svg_width}" height="{svg_height}">
            <rect x="0" y="0" width="{svg_width}" height="{svg_height}" rx="10" ry="10"
                style="fill: #f0f0f0; stroke: #ccc; stroke-width: 1"/>
            <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle"
                style="font-size: 14px; fill: #333;">{val_str}</text>
        </svg>""",
        layout=Layout(width="fit-content"),
        style={"overflow": "hidden"},
    )


def make_svg_card(key_str: str, val_str: str, *, svg_height: int = 72) -> widgets.HTML:
    max_value = max(len(key_str), len(val_str)) + 3
    key_str = _strip_and_shorten(key_str, max_value_length=max_value)
    val_str = _strip_and_shorten(val_str, max_value_length=max_value)
    svg_width = (max_value * 8) + 10
    return widgets.HTML(
        value=f"""<svg width="{svg_width}" height="{svg_height}">
            <rect x="0" y="0" width="{svg_width}" height="{svg_height}" rx="10" ry="10"
                style="fill: #517891; stroke: #ccc; stroke-width: 1"/>
            <rect x="0" y="{svg_height // 2}" width="{svg_width}" height="{svg_height // 2}" rx="10" ry="10"
                style="fill: #ADD8E6; stroke: #ADD8E6; stroke-width: 2"/>
            <text x="50%" y="25%" dominant-baseline="middle" text-anchor="middle"
                style="font-size: 14px; fill: #ffffff;">{key_str}</text>
            <text x="50%" y="75%" dominant-baseline="middle" text-anchor="middle"
                style="font-size: 14px; fill: #333;">{val_str}</text>
        </svg>""",
        layout=Layout(width="fit-content"),
        style={"overflow": "hidden"},
    )


class CommaSeparatedText(widgets.Text):
    @property
    def values(self) -> list[str]:
        """Alias for value property."""
        return [item.strip() for item in super().value.split(",") if item.strip()]


class CommaSeparatedTextBox(widgets.HBox):
    """A text box that accepts comma-separated values."""

    def __init__(self, text: CommaSeparatedText):
        self.text = text
        text_box = widgets.Box(
            children=[text],
            layout=Layout(
                width="100%", min_width="360px", max_width="640px", overflow="auto"
            ),
            style={
                "align_items": "center",
                "flex_flow": "row wrap",
                "justify_content": "flex-start",
            },
        )
        self.preview_box = widgets.HBox(
            children=[],
            layout=Layout(
                width="100%", min_width="360px", max_width="480px", overflow="auto"
            ),
            style={
                "align_items": "center",
                "flex_flow": "row wrap",
                "justify_content": "flex-start",
            },
        )

        def update_preview(_: Any) -> None:
            """Update the preview box with the current value of the text box."""
            self.preview_box.children = tuple(map(_make_svg_label, self.text.values))

        update_preview(None)
        self.text.observe(update_preview, names="value", type="change")

        super().__init__(
            children=[text_box, self.preview_box], layout=Layout(width="100%")
        )

    @property
    def value(self) -> list[str]:
        return self.text.values


def make_help_text(text: str) -> widgets.HTML:
    """Create a help text widget."""
    return widgets.HTML(
        value=f"<p style='margin: 10px; font-size: 14px; color: gray;'>{text}</p>",
        layout=Layout(width="auto"),
        style={"overflow": "auto"},
    )


class AddressBox(widgets.HBox):
    def __init__(self):
        self.checkbox = widgets.Checkbox(
            value=False, description="Enable Editing", layout=Layout(width="20%")
        )
        self.address = widgets.Text(
            value=get_default_backend_address(),
            description="Scicat Address",
            layout=Layout(width="500px"),
            style=default_style,
            disabled=True,
        )

        def toggle_editing(_: Any) -> None:
            self.address.disabled = not self.checkbox.value

        self.checkbox.observe(toggle_editing, names="value")
        super().__init__(
            children=[self.address, self.checkbox],
            layout=Layout(width="100%", min_width="560px"),
            style=default_style,
        )

    @property
    def value(self) -> str:
        return self.address.value


class CredentialWidget(widgets.VBox):
    def __init__(self, *, output: widgets.Output):
        self.output = output
        help_text = make_help_text(
            "Go to <a href='https://staging.scicat.ess.eu/user' "
            "target='_blank' style='color: blue;'>"
            "your profile</a> to find your SciCat token. "
            "(You might need to log in first.)<br>"
        )
        with self.output:
            self.address_box = AddressBox()
            self.token = widgets.Password(
                value=get_default_token(),
                placeholder="Enter token copied from SciCat",
                description="Scicat Token",
                layout=Layout(width="500px"),
                style=default_style,
            )

        super().__init__(
            children=[help_text, self.address_box, self.token],
            titles=["Credentials"],
            layout=default_layout,
            style=default_style,
        )

    def dataset_url(self, pid: str) -> str:
        pid = pid.replace("/", "%2F")
        client_url = get_default_client_address()
        return f"{client_url}/datasets/{pid}"

    @property
    def client(self) -> Client:
        from scitacean.transfer.copy import CopyFileTransfer

        return Client.from_token(
            url=self.address_box.value,
            token=self.token.value,
            file_transfer=CopyFileTransfer(),  # Not setting source_folder here
        )


def confirm_message(
    main_window,
    *,
    callback_for_confirm: Callable | None = None,
    message: str | widgets.Widget,
) -> None:
    button_layout = Layout(width="50%", height="150px", margin="20px")
    button_style = {"font_weight": "bold", "font_size": "28px"}
    confirm_button = widgets.Button(
        description="Confirm",
        tooltip="Go ahead!",
        layout=button_layout,
        style=button_style,
    )
    confirm_button.button_style = "warning"

    message_widget = (
        message
        if isinstance(message, widgets.Widget)
        else widgets.Label(
            value=f"\n \n {message}",
            layout=Layout(width="auto", display="flex", justify_content="center"),
            style={"font_weight": "bold", "font_size": "24px"},
        )
    )
    confirm_box = widgets.VBox(
        children=[message_widget, confirm_button],
        layout=Layout(width="100%", justify_content="center"),
        style=default_style,
    )
    original_children = main_window.children
    main_window.children = (confirm_box,)

    def confirm_action(_) -> None:
        main_window.children = original_children
        if callback_for_confirm is not None:
            callback_for_confirm()

    confirm_button.on_click(confirm_action)


def confirm_choice(
    main_window,
    *,
    callback_for_confirm: Callable | None = None,
    callback_for_cancel: Callable | None = None,
    message: str | widgets.Widget = "Are you sure you want to proceed?",
) -> None:
    button_layout = Layout(width="50%", height="150px", margin="20px")
    button_style = {"font_weight": "bold", "font_size": "28px"}
    confirm_button = widgets.Button(
        description="Confirm",
        tooltip="Go ahead!",
        layout=button_layout,
        style=button_style,
    )
    confirm_button.button_style = "primary"
    cancel_button = widgets.Button(
        description="Cancel",
        tooltip="Cancel and go back to the previous page.",
        layout=button_layout,
        style=button_style,
    )
    cancel_button.button_style = "warning"

    message_widget = (
        message
        if isinstance(message, widgets.Widget)
        else widgets.Label(
            value=f"\n \n {message}",
            layout=Layout(width="auto", display="flex", justify_content="center"),
            style={"font_weight": "bold", "font_size": "24px"},
        )
    )
    button_box = widgets.HBox(
        children=[cancel_button, confirm_button],
        layout=Layout(width="100%", justify_content="center"),
        style=default_style,
    )
    confirm_box = widgets.VBox(
        children=[message_widget, button_box],
        layout=Layout(width="100%", justify_content="center"),
        style=default_style,
    )
    original_children = main_window.children
    main_window.children = (confirm_box,)

    def confirm_action(_) -> None:
        main_window.children = original_children
        if callback_for_confirm is not None:
            callback_for_confirm()

    def cancel_action(_) -> None:
        main_window.children = original_children
        if callback_for_cancel is not None:
            callback_for_cancel()

    confirm_button.on_click(confirm_action)
    cancel_button.on_click(cancel_action)


# Shared Singleton Objects


def build_output_widget() -> widgets.Output:
    output = widgets.Output(
        layout=Layout(
            overflow="scroll",
            overflow_y="auto",
            flex_flow="row",
            width="auto",
            display="flex",
            height="auto",
            marging="10px",
            padding="10px",
            max_height="200px",
        ),
        style=default_style,
    )
    output.layout.border = "1px solid black"
    output.clear_output()
    return output


def get_logger() -> logging.Logger:
    """Get a logger for the SciCat widget."""
    return logging.getLogger("scicat-widget")
