import pathlib
import os
import logging
from typing import Any
from functools import partial
from dataclasses import dataclass, replace, field
from types import MappingProxyType
from collections.abc import Callable, Mapping

from ipywidgets import widgets, Layout
from IPython.display import display
from scitacean import Client, Dataset, DatasetType, RemotePath

default_layout = Layout(width="auto", min_width="560px")
default_style = {"description_width": "200px"}
button_layout = Layout(width="100%", height="36px", margin="5px")


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
            logging.getLogger("scicat-widget").warning(e)
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


_DEBUGGING_FILE_PATH = pathlib.Path("./SCICAT_WIDGET_DEBUGGING")


def _is_debugging() -> bool:
    return _DEBUGGING_FILE_PATH.exists()


def _get_debug_config() -> dict:
    """Get debugging configuration or defaults."""
    if _is_debugging():
        import yaml

        return yaml.safe_load(_DEBUGGING_FILE_PATH.read_text())
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


class CredentialBox(widgets.VBox):
    def __init__(self, *, output: widgets.Output):
        self.output = output
        with self.output:
            self.address_box = AddressBox()
            self.token = NotSoLongButNotShortText(
                value=_get_default_token(),
                placeholder="Enter token copied from SciCat",
                description="Scicat Token",
                layout=Layout(width="500px"),
                style=default_style,
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


def _get_cache_directory() -> pathlib.Path:
    """Get the cache directory for SciCat widgets."""
    cache_dir = pathlib.Path.home() / ".cache" / "scicat_widgets"
    if not cache_dir.exists():
        cache_dir.mkdir(parents=True, exist_ok=False)
    return cache_dir


def _load_public_personal_info() -> dict[str, str]:
    """Load public personal information from a YAML file."""
    import yaml

    cache_dir = _get_cache_directory()
    file_path = cache_dir / "public_personal_info.yaml"
    if file_path.exists():
        with open(file_path, "r") as file:
            return yaml.safe_load(file)
    return {}


def _make_help_text(text: str) -> widgets.HTML:
    """Create a help text widget."""
    return widgets.HTML(
        value=f"<p style='margin: 10px; font-size: 14px; color: gray;'>{text}</p>",
        layout=Layout(width="auto"),
        style={"overflow": "auto"},
    )


class PublicPersonalInfoBox(widgets.VBox, widgets.ValueWidget):
    """Box for public and personal information."""

    @dataclass(kw_only=True)
    class PublicPersonalInfo:
        """Dataclass for public personal information."""

        name: str = field(default_factory=lambda: os.environ.get("USER", ""))
        email: str = ""
        orcid: str = ""

        @classmethod
        def from_cache(cls) -> "PublicPersonalInfoBox.PublicPersonalInfo":
            """Load public personal information from cache."""
            loaded_info = _load_public_personal_info()
            return cls(
                name=loaded_info.get("name", ""),
                email=loaded_info.get("email", ""),
                orcid=loaded_info.get("orcid", ""),
            )

    def __init__(self, *, output: widgets.Output | None = None):
        self.output = output or widgets.Output()
        loaded_info = _load_public_personal_info()
        help_text = _make_help_text(
            "This information will automatically fill some of the next section, <b>Prepare Upload</b>.<br>"
            "Click <b>Save</b> button to store it in <i>~/.cache/scicat_widgets/public_personal_info.yaml</i>."
        )
        text_box = partial(
            widgets.Text, layout=default_layout, style={"description_width": "100px"}
        )
        self.name = text_box(
            value=loaded_info.get("name", ""),
            description="🪪 Name",
            placeholder="Enter your name",
        )
        self.email = text_box(
            value=loaded_info.get("email", ""),
            description="📧 Email",
            placeholder="Enter your email",
        )
        self.orcid = text_box(
            value=loaded_info.get("orcid", ""),
            description="🌳 ORCID ID",
            placeholder="Enter your ORCID ID",
        )
        input_box = widgets.VBox(
            children=[self.name, self.email, self.orcid],
            layout=Layout(width="100%", min_width="560px"),
            style=default_style,
        )

        self.save_button = widgets.Button(
            description="Save",
            tooltip="Save the public personal information. "
            "It will be saved in '~/.cache/scicat_widgets/public_personal_info.yaml'",
            layout=Layout(width="100%", height="90px"),
            style={"font_weight": "bold", "font_size": "36px"},
        )
        self.save_button.button_style = "primary"

        input_box = widgets.HBox(
            children=[input_box, self.save_button],
            layout=Layout(width="100%", justify_content="space-between"),
            style=default_style,
        )
        self.save_button.on_click(self.save_action)

        super().__init__(
            children=[help_text, input_box],
            titles=["Public Personal Information"],
            layout=Layout(width="auto", min_width="560px", margin="5px"),
            style=default_style,
        )

    def _save_action(self):
        """Action to perform when the 'Save' button is clicked."""
        import yaml

        # Save the public personal information to a file
        cache_dir = _get_cache_directory()
        file_path = cache_dir / "public_personal_info.yaml"
        public_info = {
            "name": self.name.value.strip(),
            "email": self.email.value.strip(),
            "orcid": self.orcid.value.strip(),
        }
        with open(file_path, "w") as file:
            yaml.dump(public_info, file)

    def save_action(self, _):
        """Action to perform when the 'Save' button is clicked."""
        import time

        # Change the color of the button to indicate saving
        self.save_button.button_style = ""
        self.save_button.disabled = True

        self._save_action()
        time.sleep(0.5)

        # Show a success message
        self.save_button.description = "Saved! ✅"
        self.save_button.button_style = "success"

        time.sleep(1)

        # Change the color of the button back to primary
        self.save_button.description = "Save"
        self.save_button.disabled = False
        self.save_button.button_style = "primary"

    def __del__(self) -> None:
        """Save the public personal information when the widget is deleted."""
        self._save_action()
        return super().__del__()

    @property
    def value(self) -> PublicPersonalInfo:
        """Return the public personal information as a dictionary."""
        return self.PublicPersonalInfo(
            name=self.name.value.strip(),
            email=self.email.value.strip(),
            orcid=self.orcid.value.strip(),
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
    MappingProxyType(
        {
            "type": (_to_read_only,),
            "source_folder": (_to_read_only,),
            "proposal_id": (_to_read_only,),
        }
    )
)


def _format_orcid(orcid: str) -> str:
    if not orcid.startswith("https://orcid.org/"):
        orcid = f"https://orcid.org/{orcid}"
    return orcid


def _make_default_dataset(
    my_info: PublicPersonalInfoBox.PublicPersonalInfo | None = None,
) -> Dataset:
    _my_info = my_info or PublicPersonalInfoBox.PublicPersonalInfo.from_cache()
    my_name = _my_info.name
    email = _my_info.email
    orcid = _format_orcid(_my_info.orcid)
    proposal_id = _get_current_proposal()
    source_folder = pathlib.Path(
        _get_default_proposal_mount() / proposal_id / "derived"
    ).absolute()

    return Dataset(
        type=DatasetType.DERIVED,
        contact_email=email,
        investigator=my_name,
        owner=my_name,
        owner_email=email,
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
        orcid_of_owner=orcid,
    )


def _make_default_value_registry(
    default_dataset: Dataset | None = None,
) -> MappingProxyType[str, Any]:
    """Create a default value registry for dataset fields."""

    default_dataset = default_dataset or _make_default_dataset()
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


def _replace_field(
    field_spec: Dataset.Field,
    *,
    registry: Mapping[str, tuple[Callable, ...]] = _FieldReplacementRegistry,
    default_value_registry: Mapping[str, Any] = _make_default_value_registry(),
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
        default_value=default_value_registry.get(field_spec.name, None),
    )


_FieldWidgetFactoryRegistry: MappingProxyType[
    str, Callable[[Field], widgets.ValueWidget]
] = MappingProxyType({})
_SkippedFields: tuple[str, ...] = (
    "access_groups",
    "api_version",
    "classification",
    "comment",
    "contact_email",
    "created_at",
    "created_by",
    "creation_location",
    "creation_time",
    "data_quality_metrics",
    "data_format",
    "input_datasets",
    "instrument_group",
    "is_published",
    "end_time",
    "start_time",
    "pid",
    "lifecycle",
    "license",
    "relationships",
    "updated_at",
    "updated_by",
    "validation_status",
    "run_number",
    "shared_with",
    "source_folder_host",
    "validation_status",
    "investigator",
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


def _make_svg_card(key_str: str, val_str: str, *, svg_height: int = 72) -> widgets.HTML:
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


def _fallback_field_widget_factory(field_spec: Field) -> widgets.ValueWidget:
    """
    Fallback factory for field widgets.
    It creates a Text widget for fields that do not have a specific factory.
    """
    from typing import get_origin

    field_style = {"description_width": "200px"}
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
        value = field_spec.default_value.posix
    else:
        value = str(field_spec.default_value or "")

    return widgets.Text(
        value=value,
        description=field_spec.name,
        disabled=field_spec.read_only,
        layout=Layout(width="100%", margin="5px"),
        style=field_style,
    )


class ReadonlyFieldTable(widgets.HBox):
    """A table to display read-only fields in a dataset."""

    def __init__(self, field_specs: Mapping[str, Field]):
        """Initialize the ReadonlyFieldTable with field specifications."""
        self.field_specs = field_specs
        table = self.create_table()
        label = widgets.HTML(
            value="<b>Static Fields</b>",
            layout=Layout(
                width="auto",
                text_align="center",
                justify_content="center",
                margin="25px",
            ),
            style={"font_size": "16px", "font_weight": "bold"},
        )
        super().__init__(
            children=[label, *table], layout=Layout(width="auto"), style=default_style
        )

    def create_table(self) -> list[widgets.HTML]:
        """Create a VBox containing the read-only fields."""

        def _format_value(field_spec: Field) -> str:
            """Format the value for display."""
            if isinstance(field_spec.default_value, RemotePath):
                return field_spec.default_value.posix
            elif isinstance(field_spec.default_value, list):
                return ", ".join(map(str, field_spec.default_value))
            return str(field_spec.default_value)

        return [
            _make_svg_card(field_spec.name, _format_value(field_spec))
            for field_spec in self.field_specs.values()
            if field_spec.read_only
        ]

    @property
    def value(self) -> Mapping[str, Any]:
        """Return the values of the read-only fields as a mapping."""
        return {
            field_spec.name: field_spec.default_value
            for field_spec in self.field_specs.values()
            if field_spec.read_only
        }


class DatasetFieldWidget(widgets.VBox):
    """Dataset Field Widget for Uploading."""

    def __init__(self, *, public_personal_info: PublicPersonalInfoBox | None = None):
        if public_personal_info is None:
            _default_value_registry = _make_default_value_registry()
        else:
            default_dataset = _make_default_dataset(public_personal_info.value)
            _default_value_registry = _make_default_value_registry(default_dataset)

        self.field_specs = {
            field_spec.name: _replace_field(
                field_spec, default_value_registry=_default_value_registry
            )
            for field_spec in Dataset._FIELD_SPEC
        }
        self.field_widgets: dict[str, widgets.ValueWidget] = {
            field_name: _FieldWidgetFactoryRegistry.get(
                field_name, _fallback_field_widget_factory
            )(field_spec)
            for field_name, field_spec in self.field_specs.items()
            if field_name not in _SkippedFields and not field_spec.read_only
        }
        self.static_fields: ReadonlyFieldTable = ReadonlyFieldTable(
            {
                name: field
                for name, field in self.field_specs.items()
                if name not in _SkippedFields and field.read_only
            }
        )

        super().__init__(
            [
                self.static_fields,
                *(widgets.Box([wg]) for wg in self.field_widgets.values()),
            ]
        )

    @property
    def dataset(self) -> Dataset:
        """Convert the field widgets to a Dataset instance.
        This method collects the values from the field widgets and creates a Dataset.
        """
        field_values = {
            field_name: widget.value
            for field_name, widget in self.field_widgets.items()
        }
        field_values.update(self.static_fields.value)
        owner_group = field_values.get("proposal_id", "")
        access_groups = [owner_group]
        investigator = field_values.get("owner", "")
        contact_email = field_values.get("owner_email", "")
        return Dataset(
            **field_values,
            access_groups=access_groups,
            contact_email=contact_email,
            investigator=investigator,
        )


class FileSelectionWidget(widgets.VBox):
    """Widget for selecting files to upload."""

    def __init__(self, *, output: widgets.Output):
        self.output = output
        self.file_path = widgets.Text(
            description="File Path",
            placeholder="Enter the path to the file to upload",
            layout=Layout(width="auto", margin="5px"),
            style=default_style,
        )
        self.file_path.style.description_width = "200px"
        self.file_path.style.background = "lightyellow"

        def validate_path(_) -> None:
            """Validate the file path and update the output widget."""
            file_path = pathlib.Path(self.file_path.value.strip())
            if not file_path.exists() or not file_path.is_file():
                self.file_path.style.background = "pink"
            else:
                self.file_path.style.background = "lightgreen"

        self.file_path.observe(validate_path, names="value", type="change")
        super().__init__(
            children=[self.file_path], layout=Layout(width="auto"), style=default_style
        )


class UploadBox(widgets.VBox):
    def __init__(
        self,
        *,
        credential_box: CredentialBox,
        output_widget: widgets.Output,
        public_personal_info_box: PublicPersonalInfoBox,
        file_selection_widget: FileSelectionWidget,
        **kwargs,
    ):
        default_button_layout = Layout(width="100%", height="36px", margin="5px")

        main_help_text = _make_help_text(
            "Fill the mandatory fields below to create a dataset.<br>"
            "Some fields are pre-filled and ineditable."
        )
        self.status_help_box = widgets.HBox(children=[])
        help_text_box = widgets.HBox(
            children=[main_help_text, self.status_help_box], layout=Layout(width="100%")
        )

        self.output = output_widget
        self.credential_box = credential_box
        self.public_personal_info_box = public_personal_info_box
        self.file_selection_widget = file_selection_widget

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
        self.reset_button.on_click(self.reset)
        self.upload_button.on_click(self.upload)

        self.dataset_field_widget: DatasetFieldWidget = DatasetFieldWidget()
        self.input_box = widgets.VBox(
            [
                self.dataset_field_widget,
                self.file_selection_widget,
                widgets.Box([self.reset_button, self.upload_button]),
            ],
            layout=Layout(width="auto"),
        )

        super().__init__([help_text_box, self.input_box], **kwargs)
        self._update_status_help_box()

    def _update_status_help_box(self, _=None) -> None:
        def _check_sync(
            public_info: PublicPersonalInfoBox.PublicPersonalInfo, dset: Dataset
        ) -> bool:
            """Check if the public personal info is in sync with the dataset."""
            return (
                dset.owner == public_info.name
                and dset.owner_email == public_info.email
                and dset.orcid_of_owner == _format_orcid(public_info.orcid)
            )

        public_info = self.public_personal_info_box.value
        cur_dset = self.dataset_field_widget.dataset

        if _check_sync(public_info, cur_dset):
            status_help_text = widgets.HTML(
                value="<p style='margin: 10px; font-size: 14px; color: green;'>"
                "✅ <b>Public Personal Info</b> is in sync with the dataset.</p>",
                layout=Layout(width="100%", text_align="center"),
            )

        else:
            status_help_text = widgets.HTML(
                value="<p style='margin: 10px; font-size: 14px; color: orange;'>"
                "🤔 <b>Public Personal Info</b> is NOT in sync with the dataset.<br>"
                "Press <b>Fill from Public Info</b> button to update the dataset fields.</p>",
                layout=Layout(width="100%", text_align="center"),
            )
            button = widgets.Button(
                description="Fill from Public Info",
                tooltip="Fill the dataset fields with the public personal info.",
                layout=Layout(width="auto", height="36px", margin="5px", min_width="200px", align_self="center"),
                style=default_style,
            )
            button.button_style = "warning"

            def _refill_fields(_) -> None:
                """Refill the dataset fields with the public personal info."""
                field_widgets = self.dataset_field_widget.field_widgets
                field_widgets["owner"].value = public_info.name
                field_widgets["owner_email"].value = public_info.email
                field_widgets["orcid_of_owner"].value = _format_orcid(public_info.orcid)
                self._update_status_help_box()

            button.on_click(_refill_fields)
            status_help_text = widgets.HBox(children=[status_help_text, button])

        self.status_help_box.children = (status_help_text,)

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
            self.dataset_field_widget = DatasetFieldWidget(
                public_personal_info=self.public_personal_info_box
            )
            self.input_box.children = [
                self.dataset_field_widget,
                widgets.Box([self.reset_button, self.upload_button]),
            ]

        self.confirm_choice(
            message="Are you sure you want to OVERWRITE "
            "all fields with default values?",
            callback_for_confirm=reset_action,
        )

    def upload(self, _) -> None:
        """
        Action to perform when the 'Upload' button is clicked.
        It should upload the dataset to SciCat.
        """
        dataset: Dataset = self.dataset_field_widget.dataset
        if file_path := self.file_selection_widget.file_path.value.strip():
            dataset.add_local_files(file_path)

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
        public_personal_info_box: PublicPersonalInfoBox | None = None,
        download_widget: DownloadBox | None = None,
        upload_widget: UploadBox | None = None,
    ):
        self.public_personal_info_box = public_personal_info_box
        self.upload_widget = upload_widget
        self.download_widget = download_widget
        self.credentials = credential_box

        self._sub_widgets = {
            "Credentials": self.credentials,
            "Public Personal Info": self.public_personal_info_box,
            "Prepare Upload": self.upload_widget,
            "Download": self.download_widget,
        }

        self.tabs = {
            name: widget
            for name, widget in self._sub_widgets.items()
            if widget is not None  # Only include non-None widgets
        }
        self.menus = widgets.Tab(
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

        if upload_widget is not None:
            # Update status whenever the upload widget is changed
            self.menus.observe(
                upload_widget._update_status_help_box,
                names="selected_index",
                type="change",
            )


def _config_logger():
    import logging

    try:
        from rich.logging import RichHandler

        handler = RichHandler()
    except ImportError:
        handler = logging.StreamHandler()

    logger = logging.getLogger("scicat-widget")
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


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
    return output


def download_widget(
    download_registry: dict | None = None, show: bool = True
) -> ScicatWidget:
    download_registry = download_registry or {}

    output = build_output_widget()
    credential_box = CredentialBox(output=output)
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
    _config_logger()
    output = build_output_widget()
    credential_box = CredentialBox(output=output)
    file_selection_widget = FileSelectionWidget(output=output)
    public_personal_info_box = PublicPersonalInfoBox(output=output)
    widget = ScicatWidget(
        credential_box=credential_box,
        output_widget=output,
        upload_widget=UploadBox(
            credential_box=credential_box,
            output_widget=output,
            file_selection_widget=file_selection_widget,
            public_personal_info_box=public_personal_info_box,
        ),
        public_personal_info_box=public_personal_info_box,
    )
    if show:
        display(widget)
    return widget


def scicat_widget(
    *, download_registry: dict | None = None, show: bool = True
) -> ScicatWidget:
    """Create a SciCat widget with both download and upload functionality."""
    _config_logger()
    output = build_output_widget()
    credential_box = CredentialBox(output=output)
    download_widget_instance = DownloadBox(
        credential_box=credential_box,
        output_widget=output,
        download_registry=download_registry or {},
    )
    upload_widget_instance = UploadBox(
        credential_box=credential_box,
        output_widget=output,
        file_selection_widget=FileSelectionWidget(output=output),
    )

    widget = ScicatWidget(
        credential_box=credential_box,
        output_widget=output,
        download_widget=download_widget_instance,
        upload_widget=upload_widget_instance,
    )
    if show:
        display(widget)
    return widget
