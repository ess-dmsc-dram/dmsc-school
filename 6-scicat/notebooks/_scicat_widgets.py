import pathlib
import os
import logging
from typing import Any
from functools import partial
from dataclasses import dataclass, replace
from types import MappingProxyType
from collections.abc import Callable, Mapping

from ipywidgets import widgets, Layout
from IPython.display import display
from scitacean import Client, Dataset, DatasetType, RemotePath

default_layout = Layout(width="auto")
default_style = {"description_width": "auto"}
button_layout = Layout(width="100%", height="36px", margin="5px")
text_layout = Layout(width="100%", margin="5px")
wide_text_layout = Layout(
    width="100%", min_width="360px", overflow="auto", margin="5px"
)
field_style = {"description_width": "200px"}


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
        )
        self.copy_button = widgets.Button(
            description="Copy", tooltip="Copy to clipboard", layout=Layout(width="80px")
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
        return self.text.disabled

    @disabled.setter
    def disabled(self, new_value: bool) -> None:
        self.text.disabled = new_value

    def __str__(self) -> str:
        return self.text


_DEBUGGING_FILE_PATH = pathlib.Path("./SCICAT_WIDGET_DEBUGGING")


def _is_debugging() -> bool:
    return _DEBUGGING_FILE_PATH.exists()


def _get_debug_config() -> dict:
    """Get debugging configuration or defaults."""
    if _is_debugging():
        import json

        return json.loads(_DEBUGGING_FILE_PATH.read_text())
    return {}


def _get_default_address() -> str:
    config = _get_debug_config()
    return config.get(
        "address",
        "https://staging.scicat.ess.eu/api/v3"
        if not _is_debugging()
        else "http://backend.localhost/api/v3",
    )


def _get_default_token() -> str:
    return _get_debug_config().get("token", "")


def _get_default_proposal_mount() -> pathlib.Path:
    config = _get_debug_config()
    default_path = "./myProposals/" if _is_debugging() else "/myProposals/"
    return pathlib.Path(config.get("proposal_mount", default_path))


def _get_current_proposal() -> str:
    proposal_mount = _get_default_proposal_mount()
    if not proposal_mount.exists() or not proposal_mount.is_dir():
        raise FileNotFoundError(
            f"Proposal mount path {proposal_mount} does not exist. "
            "Please check your SciCat configuration.\n"
            "Cannot find the current proposal."
        )
    # Find the first subdirectory in the proposal mount path
    sub_dirs = [sub_dir for sub_dir in proposal_mount.iterdir() if sub_dir.is_dir()]
    if not sub_dirs:
        return ""
    # Return the name of the first subdirectory
    return next(iter(sub_dirs)).name


class AddressBox(widgets.HBox):
    def __init__(self):
        self.checkbox = widgets.Checkbox(
            value=False, description="Enable Editing", layout=Layout(width="20%")
        )
        self.address = NotSoLongButNotShortText(
            _get_default_address(),
            description="Scicat Address",
            layout=Layout(width="80%", min_width="300px"),
            disabled=True,
        )

        def toggle_editing(_: Any) -> None:
            self.address.disabled = not self.checkbox.value

        self.checkbox.observe(toggle_editing, names="value")
        super().__init__(
            children=[self.address, self.checkbox],
            layout=default_layout,
            style=default_style,
        )

    @property
    def value(self) -> str:
        return self.address.value


class CredentialBox(widgets.VBox):
    def __init__(self):
        self.address_box = AddressBox()
        self.token = NotSoLongButNotShortText(
            value=_get_default_token(),
            placeholder="Enter token copied from SciCat",
            description="Scicat Token",
        )
        super().__init__(
            children=[self.address_box, self.token],
            titles=["Credentials"],
            layout=default_layout,
            style=default_style,
        )

    @property
    def client(self) -> Client:
        from scitacean.transfer.copy import CopyFileTransfer

        return Client.from_token(
            url=self.address_box.value,
            token=self.token.value,
            file_transfer=CopyFileTransfer(
                source_folder=(
                    _get_default_proposal_mount() / _get_current_proposal() / "derived"
                ).as_posix()
            ),
        )


class DownloadBox(widgets.VBox):
    def __init__(
        self,
        credential_box: CredentialBox,
        output_widget: widgets.Output,
        download_registry: dict | None = None,
        **kwargs,
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
        self.download_registry = download_registry or {}

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


@dataclass(frozen=True)
class Field(Dataset.Field):
    default_value: Any = None


def _to_read_only(field: Dataset.Field) -> Dataset.Field:
    return replace(field, read_only=True)


_FieldReplacementRegistry: MappingProxyType[str, tuple[Callable, ...]] = (
    MappingProxyType({"type": (_to_read_only,)})
)


def _make_default_dataset() -> Dataset:
    my_name = os.environ.get("USER", "")
    proposal_id = _get_current_proposal()
    source_folder = pathlib.Path(
        _get_default_proposal_mount() / proposal_id / "derived"
    ).absolute()

    return Dataset(
        type=DatasetType.DERIVED,
        contact_email="",
        investigator=my_name,
        owner=my_name,
        owner_email="",
        used_software=["scipp", "easyscience"],
        data_format="",
        is_published=False,
        owner_group=proposal_id,
        access_groups=[proposal_id],
        instrument_id=None,
        techniques=[],
        keywords=["DMSC Summer School 2025"],
        license="unknown",
        proposal_id=proposal_id,
        source_folder=source_folder.as_posix(),
        name="Summer School Reduced Dataset",
        description="Awesome reduced dataset from the DMSC Summer School 2025",
    )


def _make_default_value_registry() -> MappingProxyType[str, Any]:
    """Create a default value registry for dataset fields."""

    default_dataset = _make_default_dataset()
    # First create a `Dataset` instance with default values.
    # It is easier to set and validate the fields this way.
    # However, we need to convert it to a mapping of field names to default values.
    # It is more convenient to create a widget for each field with
    # mapping of field names to default values instead of a `Dataset` instance.
    # And `Dataset` instance is mutable but `MappingProxyType` is immutable.
    return MappingProxyType(
        {
            field.name: _attr
            for field in Dataset._FIELD_SPEC
            if (_attr := getattr(default_dataset, field.name, None)) is not None
        }
    )


_DefaultValueRegistry: MappingProxyType[str, Any] = _make_default_value_registry()


def _replace_field(
    field_spec: Dataset.Field,
    registry: Mapping[str, tuple[Callable, ...]] = _FieldReplacementRegistry,
) -> Field:
    """
    Replace fields in the field_specs based on the registry.
    Each field in the registry is replaced by applying the functions in the tuple.
    """
    from dataclasses import fields

    for func in registry.get(field_spec.name, ()):
        field_spec = func(field_spec)

    return Field(
        **{
            dc_field.name: getattr(field_spec, dc_field.name)
            for dc_field in fields(field_spec)
        },
        default_value=_DefaultValueRegistry.get(field_spec.name, None),
    )


_FieldWidgetFactoryRegistry: MappingProxyType[
    str, Callable[[Field], widgets.ValueWidget]
] = MappingProxyType({})
_SkippedFields: tuple[str, ...] = (
    "api_version",
    "classification",
    "created_at",
    "created_by",
    "creation_location",
    "creation_time",
    "data_quality_metrics",
    "input_datasets",
    "instrument_group",
    "is_published",
    "end_time",
    "start_time",
    "pid",
    "lifecycle",
    "relationships",
    "updated_at",
    "updated_by",
    "validation_status",
    "run_number",
    "shared_with",
    "source_folder_host",
    "validation_status",
    "principal_investigator",
    "sample_id",
    "job_log_data",
    "job_parameters",
    "instrument_id",
)


class CommaSeparatedText(widgets.Text):
    @property
    def values(self) -> list[str]:
        """Alias for value property."""
        return [item.strip() for item in super().value.split(",") if item.strip()]


def _make_svg_label(
    val_str: str, *, svg_height: int = 36, max_value_length: int = 30
) -> widgets.HTML:
    val_str = val_str.strip()
    if len(val_str) > max_value_length - 3:
        val_str = val_str[: max_value_length - 3] + "..."
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


def _fallback_field_widget_factory(
    field_spec: Field,
) -> widgets.ValueWidget:
    """
    Fallback factory for field widgets.
    It creates a Text widget for fields that do not have a specific factory.
    """
    from typing import get_origin

    if get_origin(field_spec.type) is list:
        default_value = field_spec.default_value or []
        text = CommaSeparatedText(
            value=",".join(map(str, default_value)),
            description=field_spec.name,
            disabled=field_spec.read_only,
            layout=Layout(
                width="100%", min_width="360px", overflow="auto", margin="5px"
            ),
            style=field_style,
        )
        return CommaSeparatedTextBox(text)
    elif isinstance(field_spec.default_value, RemotePath):
        return widgets.Text(
            value=field_spec.default_value.posix,
            description=field_spec.name,
            disabled=field_spec.read_only,
            layout=Layout(width="100%", margin="5px"),
            style=field_style,
        )
    else:
        return widgets.Text(
            value=str(field_spec.default_value or ""),
            description=field_spec.name,
            disabled=field_spec.read_only,
            layout=Layout(width="100%", margin="5px"),
            style=field_style,
        )


class DatasetFieldWidget(widgets.VBox):
    """Dataset Field Widget for Uploading."""

    def __init__(self):
        self.field_specs = {
            field_spec.name: _replace_field(field_spec)
            for field_spec in Dataset._FIELD_SPEC
        }
        self.field_widgets: dict[str, widgets.ValueWidget] = {
            field_name: _FieldWidgetFactoryRegistry.get(
                field_name, _fallback_field_widget_factory
            )(field_spec)
            for field_name, field_spec in self.field_specs.items()
            if field_name not in _SkippedFields
        }

        super().__init__([widgets.Box([wg]) for wg in self.field_widgets.values()])

    @property
    def dataset(self) -> Dataset:
        """Convert the field widgets to a Dataset instance.
        This method collects the values from the field widgets and creates a Dataset.
        """
        field_values = {
            field_name: widget.value
            for field_name, widget in self.field_widgets.items()
        }
        return Dataset(**field_values)


class UploadBox(widgets.VBox):
    def __init__(
        self, credential_box: CredentialBox, output_widget: widgets.Output, **kwargs
    ):
        default_button_layout = Layout(width="100%", height="36px", margin="5px")
        self.output = output_widget
        self.credential_box = credential_box
        self.start_button = widgets.Button(
            description="New Dataset",
            tooltip="Start creating a new dataset to upload",
            layout=default_button_layout,
            style=default_style,
        )
        self.start_button.button_style = "info"

        self.upload_button = widgets.Button(
            description="Upload",
            tooltip="Upload the dataset",
            layout=default_button_layout,
            style=default_style,
        )
        self.upload_button.button_style = "primary"
        self.upload_button.disabled = True

        self.reset_button = widgets.Button(
            description="Reset",
            tooltip="Reset the dataset fields",
            layout=default_button_layout,
            style=default_style,
        )
        self.reset_button.button_style = "warning"

        # Define the action for buttons
        self.start_button.on_click(self._create_new_dataset)
        self.reset_button.on_click(self.reset)
        self.upload_button.on_click(self.upload)

        self.dataset_field_widget: DatasetFieldWidget = DatasetFieldWidget()
        self.active_box = widgets.VBox(
            [
                self.dataset_field_widget,
                widgets.Box([self.reset_button, self.upload_button]),
            ],
            layout=Layout(width="auto"),
        )

        super().__init__([self.start_button], **kwargs)

    def _create_new_dataset(self, _) -> None:
        """
        Action to perform when the 'New Dataset' button is clicked.
        It should initialize a new dataset for upload.
        """
        with self.output:
            print("Creating a new dataset for upload...")

        self.upload_button.disabled = False
        except_for_myself = [
            child for child in self.children if child is not self.start_button
        ]
        self.children = (*except_for_myself, self.active_box)

    def confirm_choice(
        self,
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
        original_children = self.children
        self.children = (confirm_box,)

        def confirm_action(_) -> None:
            self.children = original_children
            if callback_for_confirm is not None:
                callback_for_confirm()

        def cancel_action(_) -> None:
            self.children = original_children
            if callback_for_cancel is not None:
                callback_for_cancel()

        confirm_button.on_click(confirm_action)
        cancel_button.on_click(cancel_action)

    def reset(self, _) -> None:
        """
        Reset the upload box to its initial state.
        This should be called when the 'Reset' button is clicked.
        """

        def reset_action() -> None:
            with self.output:
                print("Resetting all dataset fields to default values...")
            # Reset the active box to the initial state
            self.dataset_field_widget = DatasetFieldWidget()
            self.active_box.children = [
                self.dataset_field_widget,
                widgets.Box([self.reset_button, self.upload_button]),
            ]

        self.confirm_choice(
            message="Are you sure you want to RESET all dataset fields?",
            callback_for_confirm=reset_action,
        )

    def upload(self, _) -> None:
        """
        Action to perform when the 'Upload' button is clicked.
        It should upload the dataset to SciCat.
        """
        dataset = self.dataset_field_widget.dataset
        dataset_html = widgets.HTML(dataset._repr_html_())
        title = widgets.HTML("<h3>Dataset to Upload:</h3>")
        warning_msg = widgets.Label(
            value="Upload the dataset above.",
            layout=Layout(width="auto", display="flex", justify_content="center"),
            style={"font_weight": "bold", "font_size": "24px"},
        )

        def upload_action() -> None:
            logger = logging.getLogger("scicat-widget")
            with self.output:
                logger.info("Uploading dataset to SciCat...")
                try:
                    client = self.credential_box.client
                    client.upload_new_dataset_now(dataset)
                    logger.info("Dataset uploaded successfully!")
                except Exception as e:
                    logger.info(f"Failed to upload dataset: {e}")

        self.confirm_choice(
            message=widgets.VBox(
                children=[title, dataset_html, warning_msg],
                layout=Layout(width="100%", justify_content="center"),
            ),
            callback_for_confirm=upload_action,
        )


class ScicatWidget(widgets.VBox):
    def __init__(
        self,
        *,
        credential_box: CredentialBox,
        output_widget: widgets.Output,
        download_widget: DownloadBox | None = None,
        upload_widget: UploadBox | None = None,
    ):
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
            overflow="scroll",
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
    widget = ScicatWidget(
        credential_box=credential_box,
        output_widget=output,
        download_widget=DownloadBox(
            credential_box=credential_box,
            output_widget=output,
            download_registry=download_registry,
        ),
    )
    if show:
        display(widget)
    return widget


def upload_widget(show: bool = True) -> ScicatWidget:
    import logging

    try:
        from rich.logging import RichHandler

        handler = RichHandler()
    except ImportError:
        handler = logging.StreamHandler()

    logger = logging.getLogger("scicat-widget")
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    credential_box = CredentialBox()
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
    widget = ScicatWidget(
        credential_box=credential_box,
        output_widget=output,
        upload_widget=UploadBox(credential_box=credential_box, output_widget=output),
    )
    if show:
        display(widget)
    return widget


def scicat_widget(download_registry: dict | None = None) -> widgets.Widget:
    return ScicatWidget()


def validate_token(token: str) -> bool:
    """Try connecting to the SciCat API with the provided token."""
    from scitacean.util.credentials import ExpiringToken

    try:
        token_obj = ExpiringToken.from_jwt(token)
        token_obj.get_str()
        return True
    except Exception as e:
        print(f"Invalid token: {e}")
        return False
