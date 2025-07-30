import pathlib
import os
import logging
import scipp as sc
from typing import Any
from functools import partial
from dataclasses import dataclass, replace, field
from types import MappingProxyType
from collections.abc import Callable, Mapping

from ipywidgets import widgets, Layout
from IPython.display import display
from scitacean import Client, Dataset, DatasetType, RemotePath

# Types
_MetadataContainer = dict[str, str | int | float | sc.Variable]

default_layout = Layout(width="auto", min_width="560px")
default_style = {"description_width": "150px"}
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


def _get_default_backend_address() -> str:
    config = _get_debug_config()
    return config.get(
        "backend_address",
        "https://staging.scicat.ess.eu/api/v3"
        if not _is_debugging()
        else "http://backend.localhost/api/v3",
    )


def _get_default_client_address() -> str:
    config = _get_debug_config()
    return config.get(
        "client_address",
        "https://staging.scicat.ess.eu" if not _is_debugging() else "http://localhost",
    )


def _get_default_token() -> str:
    return _get_debug_config().get("token", "")


def _get_default_proposal_mount() -> pathlib.Path:
    if _is_debugging():
        # If debugging, use the path from the debugging file
        config = _get_debug_config()
        return pathlib.Path(config.get("proposal_mount", "./myProposals/"))
    else:
        # symlink path
        symlink_path = pathlib.Path.home() / "myProposals"
        return symlink_path.resolve()


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


def _make_help_text(text: str) -> widgets.HTML:
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
        self.address = NotSoLongButNotShortText(
            _get_default_backend_address(),
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
    except Exception:
        return False


class CredentialWidget(widgets.VBox):
    def __init__(self, *, output: widgets.Output):
        self.output = output
        help_text = _make_help_text(
            "Go to <a href='https://staging.scicat.ess.eu/user' "
            "target='_blank' style='color: blue;'>"
            "your profile</a> to find your SciCat token. "
            "(You might need to log in first.)<br>"
        )
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
            children=[help_text, self.address_box, self.token],
            titles=["Credentials"],
            layout=default_layout,
            style=default_style,
        )

    def dataset_url(self, pid: str) -> str:
        pid = pid.replace("/", "%2F")
        client_url = _get_default_client_address()
        return f"{client_url}/datasets/{pid}"

    @property
    def client(self) -> Client:
        from scitacean.transfer.copy import CopyFileTransfer

        return Client.from_token(
            url=self.address_box.value,
            token=self.token.value,
            file_transfer=CopyFileTransfer(),  # Not setting source_folder here
        )


def _get_human_readable_unique_folder_path(parent: pathlib.Path) -> pathlib.Path:
    """Generate a human-readable unique(within a second) folder name."""
    import os

    user_id = os.environ.get("USER", "unknown_user")
    # Get the highest numbered directory that has a prefix of "user_id_"
    existing_dirs = [
        dir_name
        for dir_name in parent.iterdir()
        if dir_name.is_dir() and dir_name.name.startswith(f"{user_id}_")
    ]
    existing_dirs.sort(key=lambda x: x.name)
    if len(existing_dirs) > 0 and len(list(existing_dirs[-1].iterdir())) == 0:
        # If the last directory is empty, use it
        return existing_dirs[-1]

    new_num = len(existing_dirs)
    new_dir = parent / f"{user_id}_{new_num:05d}"
    if not new_dir.exists():
        new_dir.mkdir(exist_ok=False)
    return new_dir


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


class PublicPersonalInfoWidget(widgets.VBox, widgets.ValueWidget):
    """Box for public and personal information."""

    @dataclass(kw_only=True)
    class PublicPersonalInfo:
        """Dataclass for public personal information."""

        name: str = field(default_factory=lambda: os.environ.get("USER", ""))
        email: str = ""
        orcid: str = ""

        @classmethod
        def from_cache(cls) -> "PublicPersonalInfoWidget.PublicPersonalInfo":
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
            "This information will automatically fill some fields in the next section, <b>Prepare Upload</b>.<br>"
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
        credential_box: CredentialWidget,
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
    my_info: PublicPersonalInfoWidget.PublicPersonalInfo | None = None,
) -> Dataset:
    _my_info = my_info or PublicPersonalInfoWidget.PublicPersonalInfo.from_cache()
    my_name = _my_info.name
    email = _my_info.email
    orcid = _format_orcid(_my_info.orcid)
    proposal_id = _get_current_proposal()
    source_folder = pathlib.Path(
        _get_default_proposal_mount() / proposal_id / "upload"
    ).absolute()
    source_folder = _get_human_readable_unique_folder_path(parent=source_folder)
    dataset_builder = partial(
        Dataset,
        type=DatasetType.DERIVED,
        contact_email=email,
        investigator=my_name,
        owner=my_name,
        owner_email=email,
        data_format="",
        is_published=False,
        owner_group=proposal_id,
        access_groups=[proposal_id],
        instrument_id=None,
        techniques=[],
        keywords=["DMSC Summer School 2025"],
        license="unknown",
        proposal_id=proposal_id,
        source_folder=source_folder.resolve().as_posix(),
        orcid_of_owner=orcid,
    )

    if _is_debugging():
        import datetime

        return dataset_builder(
            name=f"Debugging Dataset {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            description="This is a debugging dataset for the SciCat widget.",
            used_software=["scipp", "easyscience"],
        )
    else:
        return dataset_builder(name="", description="")


def _make_default_value_registry(
    default_dataset: Dataset,
) -> MappingProxyType[str, Any]:
    """Create a default value registry for dataset fields."""

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
    default_value_registry: Mapping[str, Any],
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

    field_style = {"description_width": "120px"}
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
            value="<b>Prefilled Fields</b>",
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


_FIELD_ORDER = (
    "name",
    "description",
    "keywords",
    "techniques",
    "used_software",
    "owner",
    "owner_email",
    "orcid_of_owner",
    "owner_group",
)


class DatasetFieldWidget(widgets.VBox):
    """Dataset Field Widget for Uploading."""

    def __init__(
        self, *, public_personal_info_widget: PublicPersonalInfoWidget | None = None
    ):
        if public_personal_info_widget is None:
            default_dataset = _make_default_dataset()
        else:
            default_dataset = _make_default_dataset(public_personal_info_widget.value)

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
        all_widgets = {**self.field_widgets}
        sub_widgets = [all_widgets.pop(field_name) for field_name in _FIELD_ORDER]
        # Add any remaining widgets that were not in the predefined order
        sub_widgets.extend(all_widgets.values())

        super().__init__(
            [self.static_fields, *(widgets.Box([wg]) for wg in sub_widgets)]
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
        techniques = field_values.get("techniques", [])
        if len(techniques) != 0:
            raise NotImplementedError("PID for techniques is not implemented yet.")

        return Dataset(
            **field_values,
            access_groups=access_groups,
            contact_email=contact_email,
            investigator=investigator,
        )


class FileSelectionWidget(widgets.VBox):
    """Widget for selecting files to upload."""

    class SelectedFileWidget(widgets.HBox):
        """Widget to display a selected file with options to remove it."""

        def __init__(self, file_path: pathlib.Path, remove_callback: Callable):
            file_dir = file_path.parent.as_posix()
            file_name = file_path.name
            file_path_str = f"{file_dir}/<b>{file_name}</b>"
            file_label = widgets.HTML(
                value=file_path_str,
                layout=Layout(width="auto"),
                style={"font_size": "14px"},
            )
            remove_button = widgets.Button(
                description="X",
                tooltip="Remove this file from the selection",
                layout=Layout(width="auto", margin="5px"),
                style=default_style,
            )
            remove_button.on_click(remove_callback)
            super().__init__(
                children=[file_label, remove_button],
                layout=Layout(left="132px", width="fit-content"),
            )

    def __init__(self, *, output: widgets.Output):
        self.output = output
        self.file_path_input = widgets.Text(
            description="File Path",
            placeholder="Enter the path to the file to upload",
            layout=Layout(width="auto", margin="5px", min_width="720px"),
            style=default_style,
        )
        self.file_path_input.style.description_width = "120px"
        self.file_path_input.style.background = "lightyellow"

        self.add_button = widgets.Button(
            description="Add File",
            tooltip="Add the file to the dataset",
            layout=Layout(width="auto", margin="5px"),
            style=default_style,
        )
        self.add_button.button_style = "primary"
        self.add_button.disabled = True
        self.current_files: set[pathlib.Path] = set()

        def validate_path(_) -> None:
            """Validate the file path and update the output widget."""
            if not (input_value := self.file_path_input.value.strip()):
                self.file_path_input.style.background = "lightyellow"
                self.add_button.disabled = True
                return

            file_path = pathlib.Path(input_value)
            if not file_path.exists() or not file_path.is_file():
                self.file_path_input.style.background = "pink"
                self.add_button.disabled = True
            else:
                self.file_path_input.style.background = "lightgreen"
                self.add_button.disabled = False

        def add_file_action(_) -> None:
            """Action to perform when the 'Add File' button is clicked."""
            file_path = self.file_path_input.value.strip()
            with self.output:
                self.current_files.add(pathlib.Path(file_path).resolve(strict=True))

            # Here you can add the logic to handle the file path, e.g., adding it to a dataset
            # For now, we just clear the input field
            self.file_path_input.value = ""
            self.add_button.disabled = True
            self._render_current_files()

        self.file_path_input.observe(validate_path, names="value", type="change")
        self.add_button.on_click(add_file_action)
        self.preview_box = widgets.VBox(children=[])
        self.input_box = widgets.HBox(
            children=[self.file_path_input, self.add_button],
            layout=Layout(width="auto"),
            style=default_style,
        )
        super().__init__(
            children=[self.input_box, self.preview_box],
            layout=Layout(width="auto"),
            style=default_style,
        )

    def _remove_file(self, file_path: pathlib.Path, _) -> None:
        """Remove a file from the current files set and update the preview box."""
        self.current_files.discard(file_path)
        self._render_current_files()

    def _render_current_files(self) -> None:
        """Render the current files in the preview box."""
        self.preview_box.children = [
            self.SelectedFileWidget(
                file_path, remove_callback=partial(self._remove_file, file_path)
            )
            for file_path in self.current_files
        ]

    @property
    def file_paths(self) -> list[pathlib.Path]:
        """Return the list of selected file paths."""
        return list(self.current_files)

    def reset(self) -> None:
        """Reset the file selection widget."""
        self.file_path_input.value = ""
        self.current_files.clear()
        self._render_current_files()


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


@dataclass(frozen=True, kw_only=True)
class _ScalarMetadataValue:
    """Dataclass for scalar metadata."""

    value: str
    unit: str


@dataclass(frozen=True, kw_only=True)
class _ScalarMetadata(_ScalarMetadataValue):
    """Dataclass for scalar metadata."""

    key: str


def _validate_scalar_values(value: Any) -> bool:
    return isinstance(value, (int, float, str)) or (
        isinstance(value, sc.Variable) and value.dims == ()
    )


def _filter_scalar_metadata(
    metadata: dict[str, Any], *, complain: Callable = lambda _: None
) -> dict[str, _ScalarMetadataValue]:
    left_over = {}
    for key, value in metadata.items():
        if not _validate_scalar_values(value):
            msg = f"Invalid scientific metadata from registry will be ignored: \n\t\t'{key}': {value}"
            complain(msg)
        elif isinstance(value, sc.Variable):
            left_over[key] = _ScalarMetadataValue(
                value=value.value, unit=str(value.unit)
            )
        else:
            left_over[key] = _ScalarMetadataValue(value=str(value), unit=str(None))

    return left_over


class MetadataWidget(widgets.VBox):
    class SelectedMetadataWidget(widgets.HBox):
        """Widget to display a selected file with options to remove it."""

        def __init__(self, metadata: _ScalarMetadata, remove_callback: Callable):
            metadata_str = f"<b>{metadata.key}</b>: {metadata.value} [{metadata.unit}]"
            metadata_label = widgets.HTML(
                value=metadata_str,
                layout=Layout(width="auto"),
                style={"font_size": "14px"},
            )
            remove_button = widgets.Button(
                description="X",
                tooltip="Remove this metadata from the selection",
                layout=Layout(width="auto", margin="5px"),
                style=default_style,
            )
            remove_button.on_click(remove_callback)
            super().__init__(
                children=[metadata_label, remove_button],
                layout=Layout(left="132px", width="fit-content"),
            )

    class RegistryInputWidget(widgets.HBox):
        """Widget to input scientific metadata from a registry."""

        def __init__(
            self,
            output_widget: widgets.Output,
            metadata_registry: _MetadataContainer,
        ):
            self.output = output_widget
            self._shared_container = metadata_registry
            self._original_metadata_registry = {}
            self._update_metadata_registry_from_shared_container()
            self.dropdown_menu = widgets.Dropdown(
                options=list(self._original_metadata_registry.keys()),
                description="Key",
                layout=Layout(width="auto", margin="5px"),
                style=default_style,
            )
            value_preview = widgets.Text("", description="Value", disabled=True)
            unit_preview = widgets.Text("", description="Unit", disabled=True)

            def _update_preview(_):
                """Update the value and unit preview based on the selected key."""
                selected_key = self.dropdown_menu.value
                if selected_key in self._original_metadata_registry:
                    metadata_value = self._original_metadata_registry[selected_key]
                    value_preview.value = str(metadata_value.value)
                    unit_preview.value = metadata_value.unit
                else:
                    value_preview.value = ""
                    unit_preview.value = ""

            self.dropdown_menu.observe(_update_preview, names="value", type="change")
            _update_preview(None)

            refresh_button = widgets.Button(
                description="Reload Options 🔄",
                tooltip="Reload the metadata options from the registry",
                layout=Layout(width="auto", margin="5px"),
                style=default_style,
            )
            refresh_button.on_click(
                lambda _: self._update_metadata_registry_from_shared_container()
            )
            super().__init__(
                children=[
                    self.dropdown_menu,
                    value_preview,
                    unit_preview,
                    refresh_button,
                ],
                layout=Layout(width="auto", margin="5px"),
                style=default_style,
            )

        def _update_metadata_registry_from_shared_container(self) -> None:
            logger = logging.getLogger("scicat_widgets")
            with self.output:
                valid_metadata = _filter_scalar_metadata(
                    self._shared_container, complain=logger.warning
                )
            self._original_metadata_registry = valid_metadata

        @property
        def value(self) -> _ScalarMetadata:
            """Return the selected metadata as a _ScalarMetadata instance."""
            selected_key = self.dropdown_menu.value
            metadata_value = self._original_metadata_registry[selected_key]
            return _ScalarMetadata(
                key=selected_key, value=metadata_value.value, unit=metadata_value.unit
            )

    class ArbitraryInputWidget(widgets.HBox):
        """Widget to input scientific metadata."""

        def __init__(self):
            self.key_input = widgets.Text(
                value="",
                description="Key",
                layout=Layout(width="auto", margin="5px"),
                style=default_style,
            )
            self.unit_input = widgets.Text(
                value="",
                description="Unit",
                layout=Layout(width="auto", margin="5px"),
                style=default_style,
            )
            self.value_input = widgets.Text(
                value="",
                description="Value",
                layout=Layout(width="auto", margin="5px"),
                style=default_style,
            )
            super().__init__(
                children=[self.key_input, self.value_input, self.unit_input]
            )

        @property
        def value(self) -> _ScalarMetadata:
            """Return the entered metadata as a _ScalarMetadata instance."""
            unit = self.unit_input.value.strip()
            unit = str(None) if unit == "" else unit
            return _ScalarMetadata(
                key=self.key_input.value.strip(),
                value=self.value_input.value.strip(),
                unit=unit,
            )

    def __init__(
        self,
        output_widget: widgets.Output,
        metadata_registry: _MetadataContainer,
    ):
        self._shared_container = metadata_registry
        self.output = output_widget
        self._current_metadata = {}
        self._registry_input_widget = self.RegistryInputWidget(
            output_widget=output_widget,
            metadata_registry=metadata_registry,
        )

        self._arbitrary_input_widget = self.ArbitraryInputWidget()

        self.input_tabs = widgets.Tab(
            children=[self._registry_input_widget, self._arbitrary_input_widget],
            layout=Layout(width="auto", margin="5px"),
            style=default_style,
        )
        self.input_tabs.titles = ("From Registry", "Arbitrary Input")

        add_button = widgets.Button(
            description="Add Metadata",
            tooltip="Add the metadata from the input fields",
            layout=Layout(width="64", margin="5px", height="108px"),
            style=default_style,
        )
        add_button.button_style = "primary"
        add_button.on_click(self._add_metadata_action)
        input_box = widgets.HBox(
            children=[add_button, self.input_tabs],
            layout=Layout(width="auto", height="fit-content"),
        )
        self.preview_box = widgets.VBox(
            children=[],
            layout=Layout(width="auto", height="fit-content", overflow="auto"),
        )

        super().__init__(
            [self._build_title(), input_box, self.preview_box],
            layout=Layout(width="auto"),
        )
        self.reset()

    def _add_metadata_action(self, _) -> None:
        selected_widget = self.input_tabs.selected_index
        if selected_widget == 0:  # From Registry
            metadata = self._registry_input_widget.value
        else:
            metadata = self._arbitrary_input_widget.value
            self._arbitrary_input_widget.key_input.value = ""
            self._arbitrary_input_widget.value_input.value = ""
            self._arbitrary_input_widget.unit_input.value = ""

        self._current_metadata[metadata.key] = metadata
        self._render_current_metadata()

    def _remove_metadata(self, key: str, _) -> None:
        """Remove metadata by key and update the preview box."""
        self._current_metadata.pop(key, None)
        self._render_current_metadata()

    def _build_title(self) -> widgets.HBox:
        label = widgets.HTML(
            value="<b>Scientific Metadata</b>",
            layout=Layout(
                width="auto",
                text_align="center",
                justify_content="center",
                margin="25px",
            ),
            style={"font_size": "16px", "font_weight": "bold"},
        )
        helper_text = _make_help_text(
            "Add a scientific metadata to the dataset.<br>"
            "Tip: Pass <b>metadata_registry</b> to the widget constructor.<br>"
        )
        return widgets.HBox(children=[label, helper_text])

    def _render_current_metadata(self) -> None:
        """Render the current scientific metadata in the preview box."""
        self.preview_box.children = [
            self.SelectedMetadataWidget(
                metadata,
                remove_callback=partial(self._remove_metadata, metadata.key),
            )
            for metadata in self._current_metadata.values()
        ]

    def reset(self) -> None:
        self._current_metadata.clear()
        self._render_current_metadata()

    @property
    def value(self) -> dict[str, dict[str, str]]:
        """Return the scientific metadata as a dictionary."""
        return {
            key: {"value": metadata.value, "unit": metadata.unit}
            for key, metadata in self._current_metadata.items()
        }


class PrepareUploadWidget(widgets.VBox):
    @property
    def dataset(self) -> Dataset:
        dataset: Dataset = self.dataset_field_widget.dataset
        dataset.meta = self.metadata_widget.value
        for file_path in self.file_selection_widget.file_paths:
            dataset.add_local_files(file_path)
        return dataset

    def __init__(
        self,
        *,
        output_widget: widgets.Output,
        public_personal_info_widget: PublicPersonalInfoWidget,
        file_selection_widget: FileSelectionWidget,
        metadata_widget: MetadataWidget,
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
        self.public_personal_info_widget = public_personal_info_widget
        self.file_selection_widget = file_selection_widget
        self.metadata_widget = metadata_widget

        self.reset_button = widgets.Button(
            description="Reset",
            tooltip="Reset the dataset fields",
            layout=default_button_layout,
            style=default_style,
        )
        self.reset_button.button_style = "warning"

        # Define the action for buttons
        self.reset_button.on_click(self._reset_action)

        self.dataset_field_widget: DatasetFieldWidget = DatasetFieldWidget()
        self.input_box = widgets.VBox([], layout=Layout(width="auto"))
        self._initialize_input_box()

        super().__init__([help_text_box, self.input_box], **kwargs)
        self._update_status_help_box()

    def _initialize_input_box(self) -> None:
        """Initialize the input box with the dataset field widget and other components."""
        self.input_box.children = [
            self.dataset_field_widget,
            self.file_selection_widget,
            self.metadata_widget,
            widgets.Box([self.reset_button]),
        ]

    def _update_status_help_box(self, _=None) -> None:
        def _check_sync(
            public_info: PublicPersonalInfoWidget.PublicPersonalInfo, dset: Dataset
        ) -> bool:
            """Check if the public personal info is in sync with the dataset."""
            return (
                dset.owner == public_info.name
                and dset.owner_email == public_info.email
                and dset.orcid_of_owner == _format_orcid(public_info.orcid)
            )

        public_info = self.public_personal_info_widget.value
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
                "Click <b>Fill from Public Info</b> button to update the dataset fields.</p>",
                layout=Layout(width="100%", text_align="center"),
            )
            button = widgets.Button(
                description="Fill from Public Info",
                tooltip="Fill the dataset fields with the public personal info.",
                layout=Layout(
                    width="auto",
                    height="36px",
                    margin="5px",
                    min_width="200px",
                    align_self="center",
                ),
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

    def reset(self) -> None:
        with self.output:
            logger = logging.getLogger("scicat-widget")
            logger.info("Resetting all dataset fields to default values...")
        # Reset the active box to the initial state
        self.dataset_field_widget = DatasetFieldWidget(
            public_personal_info_widget=self.public_personal_info_widget
        )
        self.file_selection_widget.reset()
        self.metadata_widget.reset()
        self._initialize_input_box()

    def _reset_action(self, _) -> None:
        """
        Reset the upload box to its initial state.
        This should be called when the 'Reset' button is clicked.
        """

        confirm_choice(
            self,
            message="Are you sure you want to OVERWRITE "
            "all fields with default values?",
            callback_for_confirm=self.reset,
        )


class UploadBox(widgets.VBox):
    def __init__(
        self,
        *,
        output_widget: widgets.Output,
        prepare_upload_widget: PrepareUploadWidget,
        credential_widget: CredentialWidget,
    ):
        main_help_text = _make_help_text(
            "Here you can see the dataset you are going to upload.<br>"
            "Click <b>Upload</b> button to upload the dataset to SciCat.<br>"
        )
        self.status_help_box = widgets.HBox(children=[])
        help_text_box = widgets.HBox(
            children=[main_help_text, self.status_help_box], layout=Layout(width="auto")
        )

        self.output = output_widget
        self.prepare_upload_box = prepare_upload_widget
        self.credential_box = credential_widget

        self.preview_box = widgets.VBox(children=[], layout=Layout(width="auto"))
        self.upload_button = self._build_button()
        self.upload_button.on_click(self.upload)

        super().__init__(
            [help_text_box, self.preview_box, self.upload_button],
            layout=Layout(width="auto", margin="5px"),
            style=default_style,
        )

    def _build_button(self) -> widgets.Button:
        upload_button = widgets.Button(
            description="Upload",
            tooltip="Upload the dataset",
            layout=Layout(width="auto", height="36px", margin="5px"),
            style=default_style,
        )
        upload_button.button_style = "primary"
        upload_button.layout.height = "72px"
        upload_button.style.font_weight = "bold"
        upload_button.style.font_size = "24px"
        return upload_button

    def _update_preview_box(self, _=None) -> None:
        self.preview_box.children = []
        try:
            dataset: Dataset = self.prepare_upload_box.dataset
            dataset_html = widgets.HTML(dataset._repr_html_())
            title = widgets.HTML("<h3>Dataset to Upload:</h3>")
            self.preview_box.children = [title, dataset_html]
        except Exception as e:
            self.preview_box.children = [
                widgets.HTML(
                    "<p style='color: red;'>Error occurred "
                    " preparing dataset for upload. "
                    "Please fill in the required fields and try again. <br>"
                    f"Error Message: <br>{e}</p>",
                )
            ]

    def _make_error_message(self, err: Exception) -> widgets.HTML:
        error_p = "<p style='color: red;'>Failed to upload dataset. Error Message:</p>"
        if not validate_token(self.credential_box.token) and ("expired" in str(err)):
            error_p += "SciCat login has expired. Go to <b>Credentials</b> tab and enter a new token."
        else:
            error_p += f"<p>{err}</p>"
        error_p += "<p>Click <b>Confirm</b> to close this message.</p>"
        return widgets.HTML(
            error_p,
            layout=Layout(width="auto", display="flex", justify_content="center"),
        )

    def _make_success_message(self, uploaded_dataset: Dataset) -> widgets.HTML:
        success_msg_p = "<p style='color: green;'>Dataset uploaded successfully!</p>"
        if (pid := uploaded_dataset.pid) is not None:
            url = self.credential_box.dataset_url(str(pid))
            success_msg_p += f"<p>Dataset URL: <a href='{url}' target='_blank' style='color: blue;'>{url}</a></p>"
        success_msg_p += "<p><b>Prepare Upload</b> tab was reset for a new dataset.</p>"
        success_msg_p += "<p>Click <b>Confirm</b> to close this message.</p>"
        return widgets.HTML(
            success_msg_p,
            layout=Layout(width="auto", display="flex", justify_content="center"),
        )

    def upload(self, _) -> None:
        """
        Action to perform when the 'Upload' button is clicked.
        It should upload the dataset to SciCat.
        """
        warning_msg = widgets.Label(
            value="Upload the dataset above. Upload cannot be undone.",
            layout=Layout(width="auto", display="flex", justify_content="center"),
            style={"font_weight": "bold", "font_size": "24px"},
        )

        def confirm_upload() -> None:
            logger = logging.getLogger("scicat-widget")
            with self.output:
                dataset: Dataset = self.prepare_upload_box.dataset
                logger.info("Uploading dataset to SciCat...")
                try:
                    client = self.credential_box.client
                    uploaded = client.upload_new_dataset_now(dataset)
                    logger.info("Dataset uploaded successfully!")
                    success_msg = self._make_success_message(uploaded)
                    self.prepare_upload_box.reset()
                    confirm_message(self, message=success_msg)
                except Exception as e:
                    logger.info(f"Failed to upload dataset: {e}")
                    logger.exception(e.__traceback__)
                    err_msg = self._make_error_message(e)

                    confirm_message(self, message=err_msg)

        confirm_msg = widgets.VBox(
            children=[self.preview_box, warning_msg],
            layout=Layout(width="100%", justify_content="center"),
        )
        confirm_choice(self, message=confirm_msg, callback_for_confirm=confirm_upload)


class ScicatWidget(widgets.VBox):
    def __init__(
        self,
        *,
        credential_box: CredentialWidget,
        output_widget: widgets.Output,
        public_personal_info_box: PublicPersonalInfoWidget | None = None,
        download_widget: DownloadBox | None = None,
        prepare_upload_widget: PrepareUploadWidget | None = None,
        upload_widget: UploadBox | None = None,
    ):
        self.public_personal_info_box = public_personal_info_box
        self.prepare_upload_widget = prepare_upload_widget
        self.upload_widget = upload_widget
        self.download_widget = download_widget
        self.credentials = credential_box

        self._sub_widgets = {
            "Credentials": self.credentials,
            "Public Personal Info": self.public_personal_info_box,
            "Prepare Upload": self.prepare_upload_widget,
            "Upload": self.upload_widget,
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
            logger = logging.getLogger("scicat-widget")
            logger.info("Here you can see the log of the SciCat widget.")

        output_box = widgets.Accordion(children=[self.output], titles=["Output (Log)"])
        output_box.selected_index = 0

        super().__init__(
            children=[self._build_header_message(), self.menus, output_box],
            layout=default_layout,
            style=default_style,
        )

        if prepare_upload_widget is not None and upload_widget is not None:

            def _sync_status_between_boxes(_) -> None:
                """Synchronize the status between the upload and prepare upload widgets."""
                upload_widget._update_preview_box()
                prepare_upload_widget._update_status_help_box()

            self.menus.observe(
                _sync_status_between_boxes, names="selected_index", type="change"
            )

    def _build_header_message(self) -> widgets.HTML:
        if self.upload_widget is not None and self.download_widget is None:
            available_menu_message = "upload"
        elif self.upload_widget is None and self.download_widget is not None:
            available_menu_message = "download"
        else:
            available_menu_message = "upload or download"

        return widgets.HTML(
            "<p><b>Scicat Widget</b> - "
            "<text style='color: gray;'>Follow the tabs from left to right "
            f"to {available_menu_message} dataset.</text></p>"
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
    credential_box = CredentialWidget(output=output)
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


def upload_widget(
    show: bool = True,
    metadata_registry: _MetadataContainer | None = None,
) -> ScicatWidget:
    _config_logger()
    output = build_output_widget()
    credential_box = CredentialWidget(output=output)
    file_selection_widget = FileSelectionWidget(output=output)
    public_personal_info_widget = PublicPersonalInfoWidget(output=output)
    metadata_widget = MetadataWidget(
        output_widget=output,
        metadata_registry=metadata_registry or {},
    )
    prepare_upload_widget = PrepareUploadWidget(
        output_widget=output,
        file_selection_widget=file_selection_widget,
        public_personal_info_widget=public_personal_info_widget,
        metadata_widget=metadata_widget,
    )
    _upload_widget = UploadBox(
        output_widget=output,
        prepare_upload_widget=prepare_upload_widget,
        credential_widget=credential_box,
    )
    widget = ScicatWidget(
        output_widget=output,
        credential_box=credential_box,
        public_personal_info_box=public_personal_info_widget,
        prepare_upload_widget=prepare_upload_widget,
        upload_widget=_upload_widget,
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
    credential_box = CredentialWidget(output=output)
    download_widget_instance = DownloadBox(
        credential_box=credential_box,
        output_widget=output,
        download_registry=download_registry or {},
    )
    prepare_upload_widget = PrepareUploadWidget(
        output_widget=output,
        file_selection_widget=FileSelectionWidget(output=output),
    )
    _upload_widget = UploadBox(
        output_widget=output,
        prepare_upload_widget=prepare_upload_widget,
        credential_widget=credential_box,
    )

    widget = ScicatWidget(
        credential_box=credential_box,
        output_widget=output,
        download_widget=download_widget_instance,
        prepare_upload_widget=prepare_upload_widget,
        upload_widget=_upload_widget,
    )
    if show:
        display(widget)
    return widget
