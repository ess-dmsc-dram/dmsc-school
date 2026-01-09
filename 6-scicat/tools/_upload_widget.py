import pathlib
import os
import scipp as sc
from typing import Any
from functools import partial
from dataclasses import dataclass, replace, field
from types import MappingProxyType
from collections.abc import Callable, Mapping

from ipywidgets import widgets, Layout
from scitacean import Dataset, DatasetType, RemotePath
from scitacean.model import Relationship, Technique

from _core_widgets import (
    confirm_choice,
    confirm_message,
    make_help_text,
    make_svg_card,
    get_current_proposal,
    is_debugging,
    fix_jupyter_path,
    get_default_backend_address,
    get_default_source_folder_parent,
    get_logger,
    default_layout,
    default_style,
    NotSoLongButNotShortText,
    CredentialWidget,
    CommaSeparatedText,
    CommaSeparatedTextBox,
)

# Types
MetadataContainer = dict[str, str | int | float | sc.Variable]


class AddressBox(widgets.HBox):
    def __init__(self):
        self.checkbox = widgets.Checkbox(
            value=False, description="Enable Editing", layout=Layout(width="20%")
        )
        self.address = NotSoLongButNotShortText(
            get_default_backend_address(),
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
    elif len(existing_dirs) > 0:
        new_num = int(existing_dirs[-1].name.split("_")[-1]) + 1
    else:
        new_num = 0

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
        help_text = make_help_text(
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
    proposal_id = get_current_proposal()
    source_folder_parent = get_default_source_folder_parent()
    source_folder = _get_human_readable_unique_folder_path(parent=source_folder_parent)
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
        keywords=["DMSC Winter School 2026"],
        license="unknown",
        proposal_id=proposal_id,
        source_folder=source_folder.resolve().as_posix(),
        orcid_of_owner=orcid,
    )

    if is_debugging():
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


class _TechniqueDropDown(widgets.Box):
    def __init__(self, **kwargs):
        self._NO_SELECTION_LABEL = ""
        field_style = {"description_width": "120px"}
        # Ref: https://expands-eu.github.io/ExPaNDS-experimental-techniques-ontology/index-en.html
        self.option_map = {
            "SANS": Technique(
                name="Small Angle Scattering",
                pid="http://purl.org/pan-science/PaNET/PaNET01124",
            ),
            "QENS": Technique(
                name="Quasi Elastic Neutron Scattering",
                pid="http://purl.org/pan-science/PaNET/PaNET01035",
            ),
            "Powder Diffraction": Technique(
                name="Powder Diffraction",
                pid="http://purl.org/pan-science/PaNET/PaNET01100",
            ),
        }
        self.selection = widgets.Dropdown(
            description="technique",
            options=[self._NO_SELECTION_LABEL] + list(self.option_map.keys()),
            style=field_style,
            layout=Layout(width="100%", margin="0px"),
        )
        box_layout = Layout(width="100%", overflow="auto", margin="5px")
        super().__init__(children=[self.selection], layout=box_layout, **kwargs)

    @property
    def value(self) -> list[Technique]:
        if self.selection.value == self._NO_SELECTION_LABEL:
            return []
        return [self.option_map[self.selection.value]]


_FieldWidgetFactoryRegistry: MappingProxyType[
    str, Callable[[Field], widgets.ValueWidget]
] = MappingProxyType({"techniques": lambda _: _TechniqueDropDown()})
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
            make_svg_card(field_spec.name, _format_value(field_spec))
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
"""The order in which the input widgets are shown."""


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
        # Custom Widget for parent dataset PID
        self.parent_dataset_pid = widgets.Text(
            description="Parent Dataset PID",
            placeholder="Enter the PID of the parent dataset (if any)",
            layout=Layout(width="auto", margin="5px", min_width="720px"),
            style={"description_width": "120px"},
        )
        all_widgets = {**self.field_widgets}
        sub_widgets = [all_widgets.pop(field_name) for field_name in _FIELD_ORDER]
        # Add any remaining widgets that were not in the predefined order
        sub_widgets.extend(all_widgets.values())
        sub_widgets.append(self.parent_dataset_pid)

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

        if parent_pid := self.parent_dataset_pid.value.strip():
            # TODO: It does not appear in the Related Dataset in the Client.
            relation = Relationship(pid=parent_pid, relationship="derived_from")
            relationships = [relation]
        else:
            relationships = []

        return Dataset(
            **field_values,
            access_groups=access_groups,
            contact_email=contact_email,
            investigator=investigator,
            relationships=relationships,
        )


def _img_preview_html(file_path: pathlib.Path) -> widgets.Image:
    """Generate an HTML preview for an image file."""
    return widgets.Image(
        value=file_path.read_bytes(), format="png", height=128, width=128
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

    def __init__(self, *, file_type: str = "file", output: widgets.Output):
        self.output = output
        self.file_path_input = widgets.Text(
            description=f"{file_type.capitalize()} Path",
            placeholder="Enter the path to the file to upload",
            layout=Layout(width="auto", margin="5px", min_width="720px"),
            style=default_style,
        )
        self.file_path_input.style.description_width = "120px"
        self.file_path_input.style.background = "lightyellow"

        self.add_button = widgets.Button(
            description=f"Add {file_type.capitalize()}",
            tooltip=f"Add the {file_type} to the dataset",
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

            file_path = fix_jupyter_path(input_value)
            if not file_path.exists() or not file_path.is_file():
                self.file_path_input.style.background = "pink"
                self.add_button.disabled = True
            else:
                self.file_path_input.style.background = "lightgreen"
                self.add_button.disabled = False

        def add_file_action(_) -> None:
            """Action to perform when the 'Add File' button is clicked."""
            file_path = self.file_path_input.value.strip()
            file_path = fix_jupyter_path(file_path)
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
        self.img_preview_box = widgets.HBox(
            children=[], layout=Layout(left="132px", width="fit-content")
        )
        super().__init__(
            children=[self.input_box, self.preview_box, self.img_preview_box],
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
        self.img_preview_box.children = [
            _img_preview_html(file_path)
            for file_path in self.current_files
            if file_path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif"}
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
    valid_metadata = {}
    for key, value in metadata.items():
        if not _validate_scalar_values(value):
            msg = f"Invalid scientific metadata from registry will be ignored: \n\t\t'{key}': {value}"
            complain(msg)
        elif isinstance(value, sc.Variable):
            valid_metadata[key] = _ScalarMetadataValue(
                value=value.value,
                # Scicat does not have concept of `None` unit.
                unit=str(value.unit) if value.unit is not None else "",
            )
        else:
            valid_metadata[key] = _ScalarMetadataValue(value=str(value), unit="")

    return valid_metadata


_METADATA_INPUT_STYLE = {"description_width": "40px"}
_METADATA_INPUT_LAYOUT = Layout(
    width="auto", margin="5px 15px 5px 15px", min_width="100px"
)


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
            metadata_registry: MetadataContainer,
        ):
            self.output = output_widget
            self._shared_container = metadata_registry
            self._original_metadata_registry = {}
            self._update_metadata_registry_from_shared_container()
            self.dropdown_menu = widgets.Dropdown(
                options=list(self._original_metadata_registry.keys()),
                description="Key",
                layout=_METADATA_INPUT_LAYOUT,
                style=_METADATA_INPUT_STYLE,
            )
            self.value_preview = widgets.Text(
                "",
                description="Value",
                disabled=False,
                layout=_METADATA_INPUT_LAYOUT,
                style=_METADATA_INPUT_STYLE,
            )
            # Unit may be overwritten by the user, so it is not disabled.
            self.unit_preview = widgets.Text(
                "",
                description="Unit",
                disabled=False,
                layout=_METADATA_INPUT_LAYOUT,
                style=_METADATA_INPUT_STYLE,
            )

            def _update_preview(_):
                """Update the value and unit preview based on the selected key."""
                selected_key = self.dropdown_menu.value
                if selected_key in self._original_metadata_registry:
                    metadata_value = self._original_metadata_registry[selected_key]
                    self.value_preview.value = str(metadata_value.value).strip()
                    self.unit_preview.value = str(metadata_value.unit).strip()
                else:
                    self.value_preview.value = ""
                    self.unit_preview.value = ""

            self.dropdown_menu.observe(_update_preview, names="value", type="change")
            _update_preview(None)

            refresh_button = widgets.Button(
                description="Reload Options 🔄",
                tooltip="Reload the metadata options from the registry",
                layout=_METADATA_INPUT_LAYOUT,
                style=_METADATA_INPUT_STYLE,
            )
            refresh_button.on_click(
                lambda _: self._update_metadata_registry_from_shared_container()
            )
            super().__init__(
                children=[
                    self.dropdown_menu,
                    self.value_preview,
                    self.unit_preview,
                    refresh_button,
                ]
            )

        def _update_metadata_registry_from_shared_container(self) -> None:
            with self.output:
                logger = get_logger()
                valid_metadata = _filter_scalar_metadata(
                    self._shared_container, complain=logger.warning
                )
            self._original_metadata_registry = valid_metadata

        @property
        def value(self) -> _ScalarMetadata:
            """Return the selected metadata as a _ScalarMetadata instance."""
            selected_key = self.dropdown_menu.value
            return _ScalarMetadata(
                key=selected_key,
                value=self.value_preview.value.strip(),  # Value may be overwritten by a user.
                unit=self.unit_preview.value.strip(),  # Unit may be overwritten by a user.
                # We decided to allow overwriting values of `value` and `unit` field
                # because users might want to just slightly change the values
                # i.e. McStas metadata parameters can have a value like: b'sample_SI',
                # which looks like a string representation of a bytes object.
                # Then we want users to be able to remove unnecessary b'' part.
            )

    class ArbitraryInputWidget(widgets.HBox):
        """Widget to input scientific metadata."""

        def __init__(self):
            self.key_input = widgets.Text(
                value="",
                description="Key",
                layout=_METADATA_INPUT_LAYOUT,
                style=_METADATA_INPUT_STYLE,
            )
            self.unit_input = widgets.Text(
                value="",
                description="Unit",
                layout=_METADATA_INPUT_LAYOUT,
                style=_METADATA_INPUT_STYLE,
            )
            self.value_input = widgets.Text(
                value="",
                description="Value",
                layout=_METADATA_INPUT_LAYOUT,
                style=_METADATA_INPUT_STYLE,
            )
            super().__init__(
                children=[self.key_input, self.value_input, self.unit_input]
            )

        @property
        def value(self) -> _ScalarMetadata:
            """Return the entered metadata as a _ScalarMetadata instance."""
            return _ScalarMetadata(
                key=self.key_input.value.strip(),
                value=self.value_input.value.strip(),
                unit=self.unit_input.value.strip(),
            )

    def __init__(
        self,
        output_widget: widgets.Output,
        metadata_registry: MetadataContainer,
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
            layout=Layout(
                width="108px", margin="5px", height="98px", min_width="108px"
            ),
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
        helper_text = make_help_text(
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
        for attachment_path in self.attachment_selection_widget.file_paths:
            dataset.add_attachment(
                attachment_path,
                caption=attachment_path.name.removesuffix(attachment_path.suffix),
            )

        return dataset

    def __init__(
        self,
        *,
        output_widget: widgets.Output,
        public_personal_info_widget: PublicPersonalInfoWidget,
        file_selection_widget: FileSelectionWidget,
        attachment_selection_widget: FileSelectionWidget,
        metadata_widget: MetadataWidget,
        **kwargs,
    ):
        default_button_layout = Layout(width="100%", height="36px", margin="5px")

        main_help_text = make_help_text(
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
        self.attachment_selection_widget = attachment_selection_widget
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
            self.attachment_selection_widget,
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
            get_logger().info("Resetting all dataset fields to default values...")
        # Reset the active box to the initial state
        self.dataset_field_widget = DatasetFieldWidget(
            public_personal_info_widget=self.public_personal_info_widget
        )
        self.file_selection_widget.reset()
        self.attachment_selection_widget.reset()
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


def validate_token(token: str) -> bool:
    """Try connecting to the SciCat API with the provided token."""
    from scitacean.util.credentials import ExpiringToken

    try:
        token_obj = ExpiringToken.from_jwt(token)
        token_obj.get_str()
        return True
    except Exception:
        return False


class UploadWidget(widgets.VBox):
    def __init__(
        self,
        *,
        output_widget: widgets.Output,
        prepare_upload_widget: PrepareUploadWidget,
        credential_widget: CredentialWidget,
    ):
        main_help_text = make_help_text(
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
            import time

            logger = get_logger()

            with self.output:
                dataset: Dataset = self.prepare_upload_box.dataset
                # Log start of the upload process
                logger.info("Uploading dataset to SciCat...")
                original_children = self.children
                temporary_page = widgets.HTML(
                    "<p style='color: blue;'>Uploading dataset to SciCat...</p>",
                    layout=Layout(
                        width="auto", display="flex", justify_content="center"
                    ),
                )
                self.children = [temporary_page]
                start = time.time()
                try:
                    # Upload the dataset
                    client = self.credential_box.client
                    uploaded = client.upload_new_dataset_now(dataset)
                    logger.info("Dataset uploaded successfully!")
                    # Log success message
                    success_msg = self._make_success_message(uploaded)
                    elapsed = time.time() - start
                    logger.info(f"Dataset upload took {elapsed:.2f} seconds.")
                    if elapsed < 1:
                        time.sleep(1 - elapsed)  # Ensure at least 1 second delay
                    # Restore the original children and show confirmation message
                    self.children = original_children
                    confirm_message(self, message=success_msg)
                    # Reset the prepare upload box for a new dataset
                    self.prepare_upload_box.reset()
                    self._update_preview_box()
                except Exception as e:
                    logger.info(f"Failed to upload dataset: {e}")
                    logger.error(e.__traceback__)
                    # Restore the original children and show error message
                    err_msg = self._make_error_message(e)
                    self.children = original_children
                    confirm_message(self, message=err_msg)

        confirm_msg = widgets.VBox(
            children=[self.preview_box, warning_msg],
            layout=Layout(width="100%", justify_content="center"),
        )
        confirm_choice(self, message=confirm_msg, callback_for_confirm=confirm_upload)
