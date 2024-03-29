import json
import argparse
from pathlib import Path
import os
from shutil import copytree, ignore_patterns

EMPTY_CELL = {
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": ["# Insert your solution:"],
}


parser = argparse.ArgumentParser(description="Remove solution cells from all notebooks")
parser.add_argument(
    "destination", type=str, help="Destination folder for collecting outputs."
)
args = parser.parse_args()


def clean(filepath, destination):
    with open(filepath, "r") as myfile:
        data = myfile.read()

    obj = json.loads(data)

    out = []
    for cell in obj["cells"]:
        if "tags" in cell["metadata"]:
            if ("solution" in cell["metadata"]["tags"]) and (
                "dmsc-school-keep" not in cell["metadata"]["tags"]
            ):
                out.append(EMPTY_CELL)
            elif ("remove-cell" in cell["metadata"]["tags"]) and (
                "dmsc-school-keep" not in cell["metadata"]["tags"]
            ):
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
        ),
        dirs_exist_ok=True,
    )
    for path in Path(".").rglob("*.ipynb"):
        print(path)
        clean(filepath=path, destination=args.destination)
