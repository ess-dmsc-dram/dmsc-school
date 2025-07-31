from _core_widgets import CredentialWidget, default_style, get_logger
import ipywidgets as widgets
from ipywidgets import Layout


class DownloadWidget(widgets.VBox):
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
                    get_logger().info(
                        f"Adding PIDs to download list: {', '.join(pids)}"
                    )

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
