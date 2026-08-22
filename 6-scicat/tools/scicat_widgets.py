"""A Jupyter widget for uploading datasets to SciCat."""

import os
import uuid

from ipywidgets import widgets, Layout
import IPython.display
from scicat_widget import DatasetUploadWidget
from scitacean import Client, Dataset
from collections.abc import Callable

_SCICAT_PROFILE = "staging.ess"

_SCHOOL_PROPOSAL = "919936"
_SCHOOL_INSTRUMENT_ID = "20.500.12269/de2b79b1-ca76-4954-b7f7-3535efaff2e2"
_SCHOOL_INSTRUMENT_NAME = "WORKSHOP"


def upload_widget(client: Client | None = None) -> DatasetUploadWidget | widgets.Output:
    """Create a widget for uploading datasets to SciCat.

    Parameters
    ----------
    client:
        The client to use for uploading datasets.
        If None, a login widget will be displayed.
    """
    if client is not None:
        return _make_dataset_upload_widget(client)

    output = widgets.Output()
    login_widget = _LoginWidget()
    login_widget.on_sign_in(_make_login_handler(output))
    with output:
        IPython.display.display(login_widget)
    return output


def _make_initial() -> Dataset:
    user = os.getlogin()
    return Dataset(
        contact_email="",
        keywords=["DMSC Summer School 2026"],
        instrument_ids=[_SCHOOL_INSTRUMENT_ID],
        owner_group=_SCHOOL_PROPOSAL,
        principal_investigators=[],
        proposal_ids=[_SCHOOL_PROPOSAL],
        source_folder=f"/ess/data/{_SCHOOL_PROPOSAL}/{_SCHOOL_INSTRUMENT_NAME.lower()}/upload/{user}/{uuid.uuid4()}",
        type="derived",
    )


_LOCKED_FIELDS = (
    "accessGroups",
    "instrumentIds",
    "ownerGroup",
    "proposalIds",
    "sourceFolder",
)


def _make_help_text(text: str) -> widgets.HTML:
    """Create a help text widget."""
    return widgets.HTML(
        value=f"<p style='margin: 10px; font-size: 14px; color: var(--jp-content-font-color1);'>{text}</p>",
        layout=Layout(width="auto"),
        style={"overflow": "auto"},
    )

class _LoginWidget(widgets.VBox):
    def __init__(self) -> None:
        help_text = _make_help_text(
            "Go to <a href='https://staging.scicat.ess.eu/user' "
            "target='_blank' style='color: var(--jp-content-link-color);'>"
            "your profile</a> to find your SciCat token. "
            "(You might need to log in first.)<br>"
        )
        self.token = widgets.Password(
            placeholder="Enter token copied from SciCat",
            description="Scicat Token",
            layout=Layout(width="500px"),
            style={"description_width": "150px"},
        )
        self.error = widgets.HTML(value="")
        self.login_button = widgets.Button(
            description='Sign in',
            disabled=True,
            button_style='info',
            tooltip='Submit token and sign in to SciCat',
            icon='check',
            style={"margin-top": "10em"},
        )

        self.token.observe(self._on_token_change, "value")

        super().__init__(
            children=[help_text, self.token, self.error, self.login_button],
            titles=["Sign in"],
            layout=Layout(width="auto", min_width="560px"),
            style={"description_width": "150px"},
        )

    def on_sign_in(self, handler: Callable[[widgets.Button, Client], None]) -> None:
        """Register a callback to execute when the user signs in."""
        def impl(button: widgets.Button) -> None:
            if not self.token.value:
                return

            try:
                client = Client.from_token(_SCICAT_PROFILE, token=self.token.value)
                client.scicat.get_proposal_model(_SCHOOL_PROPOSAL)
            except Exception as exc:
                self.error.value = f"<span style='color:var(--jp-error-color1);'>{exc.args[0]}</span>"
            else:
                handler(button, client)

        self.login_button.on_click(impl)

    def _on_token_change(self, change: dict[str, object]) -> None:
        self.login_button.disabled = not change.get("new")


def _make_dataset_upload_widget(client: Client) -> DatasetUploadWidget:
    return DatasetUploadWidget(
        client,
        initial=_make_initial(),
        locked=_LOCKED_FIELDS,
    )

def _make_login_handler(output: widgets.Output) -> Callable[[widgets.Button, Client], None]:
    def handler(button: widgets.Button, client: Client) -> None:
        button.close()
        output.clear_output()

        widget = _make_dataset_upload_widget(client)
        with output:
            IPython.display.display(widget)

    return handler
