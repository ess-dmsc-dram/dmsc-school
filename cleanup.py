# Cleanup python script to remove all siimulation and reduction outputs to start fresh.
import os
import glob
import shutil


def cleanup():
    # Go into the mcstas folder, and find all folders than contain 3 files:
    # mccode.h5, *.instr, and *.c
    # If we have a match, remove the directory.
    path = "3-mcstas"

    for root, _, files in os.walk(path):
        if len(files) != 3:
            continue

        if (
            "mccode.h5" in files
            and any(f.endswith(".instr") for f in files)
            and any(f.endswith(".c") for f in files)
        ):
            print("Removing directory:", root)
            # Use shutil.rmtree to remove the directory and its contents
            shutil.rmtree(root)

    # Go into the 4-reduction folder
    for pattern in (
        "4-reduction/*QENS*.h5",
        "4-reduction/reduced*.xye",
        "4-reduction/sans_*.dat",
    ):
        for f in glob.glob(pattern):
            print("Removing file:", f)
            os.remove(f)


if __name__ == "__main__":
    cleanup()
