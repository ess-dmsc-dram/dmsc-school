from ipywidgets import widgets, Layout
from IPython.display import display

from _core_widgets import (
    build_output_widget,
    is_debugging,
    get_logger,
    default_layout,
    default_style,
    CredentialWidget,
)
from _upload_widget import (
    PublicPersonalInfoWidget,
    PrepareUploadWidget,
    UploadWidget,
    MetadataContainer,
    MetadataWidget,
    FileSelectionWidget,
)
from _download_widget import DownloadWidget, DirectorySelectionWidget


class ScicatWidget(widgets.VBox):
    def __init__(
        self,
        *,
        credential_widget: CredentialWidget,
        output_widget: widgets.Output,
        public_personal_info_box: PublicPersonalInfoWidget | None = None,
        download_widget: DownloadWidget | None = None,
        prepare_upload_widget: PrepareUploadWidget | None = None,
        upload_widget: UploadWidget | None = None,
    ):
        self.public_personal_info_box = public_personal_info_box
        self.prepare_upload_widget = prepare_upload_widget
        self.upload_widget = upload_widget
        self.download_widget = download_widget
        self.credentials = credential_widget

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
        self.menus.selected_index = 1 if is_debugging() else 0

        self.output = output_widget
        with self.output:
            get_logger().info("Here you can see the log of the SciCat widget.")

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

    fmt = "[%(asctime)s] \033[1m%(levelname)s\033[0m %(message)s (%(filename)s:%(lineno)d)"
    formatter = logging.Formatter(fmt, datefmt="%Y-%m-%d %H:%M:%S")
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = get_logger()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def download_widget(
    download_registry: dict | None = None, show: bool = True
) -> ScicatWidget:
    output = build_output_widget()
    credential_widget = CredentialWidget(output=output)
    dir_selection_widget: DirectorySelectionWidget = DirectorySelectionWidget(
        output=output
    )
    download_widget: DownloadWidget = DownloadWidget(
        dir_selection_widget=dir_selection_widget,
        credential_widget=credential_widget,
        output_widget=output,
        download_registry=download_registry,
    )
    widget = ScicatWidget(
        credential_widget=credential_widget,
        output_widget=output,
        download_widget=download_widget,
    )
    if is_debugging():
        from _core_widgets import get_default_download_pid, get_default_target_dir

        download_widget.pid_entry.value = get_default_download_pid()
        dir_selection_widget.dir_path_input.value = get_default_target_dir()

    if show:
        display(widget)
    return widget


def upload_widget(
    show: bool = True,
    metadata_registry: MetadataContainer | None = None,
) -> ScicatWidget:
    _config_logger()
    output = build_output_widget()
    credential_widget = CredentialWidget(output=output)
    file_selection_widget = FileSelectionWidget(output=output)
    attachment_selection_widget = FileSelectionWidget(
        output=output, file_type="Attachment"
    )
    public_personal_info_widget = PublicPersonalInfoWidget(output=output)
    metadata_widget = MetadataWidget(
        output_widget=output,
        metadata_registry=metadata_registry or {},
    )
    prepare_upload_widget = PrepareUploadWidget(
        output_widget=output,
        file_selection_widget=file_selection_widget,
        attachment_selection_widget=attachment_selection_widget,
        public_personal_info_widget=public_personal_info_widget,
        metadata_widget=metadata_widget,
    )
    _upload_widget = UploadWidget(
        output_widget=output,
        prepare_upload_widget=prepare_upload_widget,
        credential_widget=credential_widget,
    )
    widget = ScicatWidget(
        output_widget=output,
        credential_widget=credential_widget,
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
    credential_widget = CredentialWidget(output=output)
    dir_selection_widget = DirectorySelectionWidget(output=output)
    download_widget_instance = DownloadWidget(
        dir_selection_widget=dir_selection_widget,
        credential_widget=credential_widget,
        output_widget=output,
        download_registry=download_registry,
    )
    file_selection_widget = FileSelectionWidget(output=output)
    attachment_selection_widget = FileSelectionWidget(output=output, file_type="Attachment")
    public_personal_info_widget = PublicPersonalInfoWidget(output=output)
    metadata_widget = MetadataWidget(
        output_widget=output,
        metadata_registry={},
    )
    prepare_upload_widget = PrepareUploadWidget(
        output_widget=output,
        file_selection_widget=file_selection_widget,
        attachment_selection_widget=attachment_selection_widget,
        public_personal_info_widget=public_personal_info_widget,
        metadata_widget=metadata_widget,
    )
    _upload_widget = UploadWidget(
        output_widget=output,
        prepare_upload_widget=prepare_upload_widget,
        credential_widget=credential_widget,
    )

    widget = ScicatWidget(
        credential_widget=credential_widget,
        output_widget=output,
        download_widget=download_widget_instance,
        prepare_upload_widget=prepare_upload_widget,
        upload_widget=_upload_widget,
    )
    if show:
        display(widget)
    return widget
