import json
import argparse

TO_BE_REMOVED = ["slideshow", "editable"]


parser = argparse.ArgumentParser(description="Clean metadata from a notebook.")
parser.add_argument("filename", type=str, help="Name of the file.")
args = parser.parse_args()


def clean(filename):
    with open(filename, "r") as myfile:
        data = myfile.read()

    obj = json.loads(data)

    for cell in obj["cells"]:
        for key in TO_BE_REMOVED:
            cell["metadata"].pop(key, None)

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1)
        f.write("\n")


if __name__ == "__main__":
    clean(args.filename)
