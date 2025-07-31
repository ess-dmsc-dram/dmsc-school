import ipywidgets as widgets
import pathlib

from collections.abc import Callable
from ipywidgets import Layout
from scitacean import Dataset, Client

from _core_widgets import (
    CredentialWidget,
    default_style,
    default_layout,
    confirm_choice,
    confirm_message,
    fix_jupyter_path,
    get_logger,
    make_help_text,
)


class DirectorySelectionWidget(widgets.VBox):
    """Widget for selecting files to upload."""

    def __init__(self, *, output: widgets.Output):
        self.output = output
        self.dir_path_input = widgets.Text(
            description="Target Directory Path",
            placeholder="Enter the path to the directory to upload",
            layout=Layout(width="auto", margin="5px", min_width="720px"),
            style=default_style,
        )
        self.dir_path_input.style.description_width = "147px"
        self.dir_path_input.style.background = "lightyellow"

        self.preview_box = widgets.VBox(children=[])
        self.render_current_selection()
        super().__init__(
            children=[self.dir_path_input, self.preview_box],
            layout=Layout(width="auto"),
            style=default_style,
        )

    def render_current_selection(self) -> None:
        """Render the current files in the preview box."""
        cur_dir = fix_jupyter_path(self.dir_path_input.value.strip())
        self.preview_box.children = [
            make_help_text(
                "The dataset will be downloaded to this directory: "
                f"<b>{cur_dir.resolve().as_posix()}</b><br>"
                "The directory should already exist."
            )
        ]

    @property
    def value(self) -> pathlib.Path:
        """Return the current directory path."""
        return fix_jupyter_path(self.dir_path_input.value.strip())


def build_dataset_preview(dataset: Dataset, title: str, desc: str = "") -> widgets.VBox:
    preview_box = widgets.VBox(children=[])
    try:
        dataset_html = widgets.HTML(dataset._repr_html_())
        title = widgets.HTML(f"<h3>{title}:</h3>")
        description = make_help_text(desc)
        preview_box.children = [title, description, dataset_html]
    except Exception as e:
        preview_box.children = [
            widgets.HTML(
                "<p style='color: red;'>Error occurred "
                " downloading dataset. <br>"
                f"Error Message: <br>{e}</p>",
            )
        ]
    return preview_box


def _download_files(
    *,
    report_to: widgets.Box,
    client: Client,
    dataset: Dataset,
    target: pathlib.Path,
    confirm_action: Callable | None = None,
    registry: dict | None = None,
) -> None:
    import time

    logger = get_logger()
    # Report the download progress to the user
    original_children = report_to.children
    report_to.children = [
        widgets.HTML(
            "<p style='color: blue; font-weight: bold;'>"
            "Downloading files from the dataset... </p>"
        )
    ]
    # Download the files from the dataset
    start = time.time()
    result = client.download_files(dataset=dataset, target=target)
    elapsed = time.time() - start
    # Report the result to the user
    logger.info(
        f"Downloaded {len(result.files)} file(s) from dataset {dataset.pid} "
        f"in {elapsed:.2f} seconds."
    )
    if elapsed < 1:
        time.sleep(1 - elapsed)  # Ensure at least 1 second delay for UI update

    report_to.children = [
        widgets.HTML("<p style='color: green; font-weight: bold;'>Done...! </p>")
    ]
    time.sleep(1)

    # Restore the original children and show the result
    desc = "Check the <b>Local</b> path of <b>Files</b> in the dataset "
    desc += "below to see where the files were downloaded."
    if isinstance(registry, dict):
        registry[dataset.pid] = target
        desc += "<br>The dataset has been added to the <b>download registry</b>."

    desc += "<br>Click <b>Confirm</b> to reset the widget and download another dataset."

    preview = build_dataset_preview(
        result, title="Dataset Files Downloaded Successfully", desc=desc
    )
    report_to.children = original_children
    confirm_message(report_to, message=preview, callback_for_confirm=confirm_action)


class DownloadWidget(widgets.VBox):
    def __init__(
        self,
        *,
        dir_selection_widget: DirectorySelectionWidget,
        credential_widget: CredentialWidget,
        output_widget: widgets.Output,
        download_registry: dict | None = None,
    ):
        self.output = output_widget
        self.dir_selection_widget = dir_selection_widget
        help_text = make_help_text(
            "Go to <a href='https://staging.scicat.ess.eu/' "
            "target='_blank' style='color: blue;'>"
            "scicat</a> to find a dataset you want to download. "
            "(You might need to log in first.)<br>"
        )
        self.credential_box = credential_widget
        self.pid_entry = widgets.Text(
            description="PID",
            placeholder="Enter the PID of a dataset to download.",
            layout=default_layout,
            style=default_style,
        )
        self.download_registry = {} if download_registry is None else download_registry
        download_button = widgets.Button(
            description="Download",
            button_style="primary",
            layout=Layout(width="auto", height="72px", margin="10px"),
            style={"font_weight": "bold", "font_size": "24px"},
        )

        def validate_path(_) -> None:
            """Validate the file path and update the output widget."""
            if not (cur_dir := dir_selection_widget.value):
                dir_selection_widget.dir_path_input.style.background = "lightyellow"
                return

            dir_selection_widget.render_current_selection()
            if not cur_dir.exists() or not cur_dir.is_dir():
                dir_selection_widget.dir_path_input.style.background = "pink"
                download_button.disabled = True
            else:
                dir_selection_widget.dir_path_input.style.background = "lightgreen"
                download_button.disabled = False

        dir_selection_widget.dir_path_input.observe(
            validate_path, names="value", type="change"
        )
        download_button.on_click(self.download)

        super().__init__(
            [help_text, self.pid_entry, dir_selection_widget, download_button]
        )

    def reset(self) -> None:
        """Reset the widget to its initial state."""
        self.pid_entry.value = ""
        self.dir_selection_widget.dir_path_input.value = ""

    def download(self, _) -> None:
        with self.output:
            try:
                client = self.credential_box.client
                dataset = client.get_dataset(pid=self.pid_entry.value.strip())
                preview = build_dataset_preview(
                    dataset,
                    title="Dataset To Be Downloaded",
                    desc="Please review the dataset details to be downloaded.<br>"
                    "Click <b>Confirm</b> to download the <b>files</b>.",
                )

                def _download() -> None:
                    with self.output:
                        _download_files(
                            report_to=self,
                            client=client,
                            dataset=dataset,
                            target=self.dir_selection_widget.value,
                            confirm_action=self.reset,
                            registry=self.download_registry,
                        )

                confirm_choice(self, message=preview, callback_for_confirm=_download)
            except Exception as e:
                get_logger().error(f"Error downloading dataset: {e}.")
                msg = widgets.HTML(
                    "<p style='color: red;'>Error occurred downloading dataset. "
                    "Please check the PID, target directory and try again. <br>"
                    f"Error Message: <br>{e}</p>",
                )
                confirm_message(self, message=msg)
