"""Helper module to sync team members work."""

import pydantic
import pathlib
import yaml
from rich.logging import RichHandler
import logging
import shutil

_MYPROPOSALS=pathlib.Path.home()/"myProposals/workshop"
_proposal = next(iter(_MYPROPOSALS.iterdir()))
PROPOSAL_DIR=(_MYPROPOSALS/_proposal).resolve()/"derived"
TEAMDIR="1-python/ess-pipeline"
MYDIR=pathlib.Path(__file__).parent


def _logger(verbose:bool=False) -> logging.Logger:
    logger = logging.getLogger("python-exercise")
    logger.addHandler(RichHandler(level=logging.DEBUG, markup=True))
    if verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    return logger


class Assignments(pydantic.BaseModel):
    # assignment-username pairs
    source: str = ""
    target: str = ""
    guide: str = ""
    sample: str = ""
    detector: str = ""


class Team(pydantic.BaseModel):
    name: str = ""
    assignments: Assignments

    def sync(
        self,
        *,
        target_dir: pathlib.Path = MYDIR,
        logger: logging.Logger = logging.getLogger("python-exercise"),
        ignore_error: bool = False
    ) -> None:
        log = logger.debug
        assignments = self.assignments.model_dump()
        for assignment, user in assignments.items():
            if user:
                log(f"Copying {assignment} module from '{user}'")
                module_path = PROPOSAL_DIR/f"{user}-workbook"/TEAMDIR/f"{assignment}.py"
                if module_path.exists():
                    try:
                        shutil.copy2(module_path, target_dir)
                        log(f"Found the '{assignment}' module in {module_path} and copied over...")
                    except shutil.SameFileError:
                        log("Skipping my file.")
                else:
                    err_msg = f"{module_path} does not exist... " + \
                    "Check the user name again in team.yml file. " + \
                    f"And make sure the user, '{user}' has their " + \
                    f"'{assignment}' moddule in their workspace."
                    if not ignore_error:
                        raise FileNotFoundError(err_msg)
                    else:
                        logger.error(err_msg)
            else:
                log(f"No user specified for module module '{assignment}'... Skipping...")


def sync_modules(verbose:bool = False) -> None:
    logger = _logger(verbose)

    config_path = pathlib.Path(__file__).parent / "team.yml"
    config = yaml.safe_load(config_path.read_text())
    team = Team(**config)
    logger.debug(f"Team Info: {team}")

    logger.debug("Synchronizing team modules...")
    team.sync(ignore_error=True)
    logger.info(
        "Copied all modules from team members. "
        "Restart the kernel of `pipeline.ipynb` and rerun the pipeline."
    )


if __name__=="__main__":
    sync_modules(verbose=True)
