import json
import argparse
from pathlib import Path
import os
from shutil import copytree, ignore_patterns

BASE_CELL = {
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
}

EMPTY_CELL = BASE_CELL.copy()
EMPTY_CELL["source"] = ["# Insert your solution:\n"]

WIDGET_CELL = BASE_CELL.copy()
WIDGET_CELL["source"] = ["%matplotlib widget"]

parser = argparse.ArgumentParser(description="Remove solution cells from all notebooks")
parser.add_argument(
    "destination", type=str, help="Destination folder for collecting outputs."
)
args = parser.parse_args()


def clean(filepath, destination, add_mpl_widget_cell=False):
    with open(filepath, "r") as myfile:
        data = myfile.read()

    obj = json.loads(data)

    out = []
    if add_mpl_widget_cell:
        out.append(WIDGET_CELL)
    for cell in obj["cells"]:
        if "tags" in cell["metadata"]:
            if ("solution" in cell["metadata"]["tags"]) and (
                "dmsc-school-keep" not in cell["metadata"]["tags"]
            ):
                out.append(EMPTY_CELL)
            elif (
                ("remove-cell" in cell["metadata"]["tags"])
                and ("dmsc-school-keep" not in cell["metadata"]["tags"])
            ) or ("dmsc-school-remove" in cell["metadata"]["tags"]):
                pass
            else:
                out.append(cell)
        else:
            out.append(cell)
    obj["cells"] = out

    outfile = os.path.join(destination, filepath)
    with open(outfile, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1)
        f.write("\n")


if __name__ == "__main__":
    copytree(
        ".",
        args.destination,
        ignore=ignore_patterns(
            ".git*",
            "*.pyc",
            "__pycache__",
            "*.ipynb_checkpoints",
            "README.md",
            "LICENSE",
            "references.bib",
            "*.html",
            "*.yml",
            "_static",
            "article",
            "clean_metadata.py",
            "glossary.md",
            "favicon.ico",
            "intro.md",
            "requirements.txt",
            "strip_solutions.py",
            "update_workbook.py",
            ".pre-commit-config.yaml",
            ".python-version",
            "requirements.in",
            "typos.toml",
        ),
        dirs_exist_ok=True,
    )
    notebooks_with_figures = ("matplotlib", "3-mcstas", "4-reduction", "5-analysis")
    for path in Path(".").rglob("*.ipynb"):
        print(path)
        if "ipynb_checkpoints" not in str(path):
            clean(
                filepath=path,
                destination=args.destination,
                add_mpl_widget_cell=any(
                    string in str(path) for string in notebooks_with_figures
                ),
            )
