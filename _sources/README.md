![dmscschoollogo](https://indico.ess.eu/event/3514/logo-1681316.png)

# DMSC School Lecture Materials
Lecture material repository for teachers at DMSC School.

## Course Directories
There are 6 courses in the summer school.
Each course has its own directory for collecting materials in this repository.

- 1-python
- 3-mcstas
- 4-reduction
- 5-analysis
- 6-scicat

## Prerequisites

Create an environment with Python 3.11 and the dependencies from `requirements.txt`.
Warning: the dependencies are pinned, so do not install them into your global environment or you risk breaking it!

## Jupyter notebooks
Many of materials are written in notebooks and are published online by `jupyter-book`.
Here are some tips and tools for writing jupyter notebooks for courses.

### Clearing output
Command to clear outputs of all jupyter notebooks in the current directory.
```bash
tree -ifF -P *.ipynb | grep .ipynb | xargs -n1 jupyter nbconvert --ClearOutputPreprocessor.enabled=True --inplace
```

### Building the book

From the root folder:

```bash
jupyter-book build -W --keep-going .
```

### Tags
Teachers can add `tags` into the each cells for building textbooks and exporting workbooks.

These are available tags handled by `jupyter-book` build or `update_workbook.py` script.

#### Jupyter-book tags
There are a few tags that are often used. See [this page](https://jupyterbook.org/en/stable/interactive/hiding.html#hide-or-remove-content) for more options.

- `hide-cell`
    Both `input` and `output` will be hidden in the published pages.
- `raise-exceptions`
    If an exception is expected to be raised from the cell.
    If you are using this tag with `remove-output` tag, consider moving this code snippet to markdown as a code block.
- `remove-output`
    `outputs` of the cell will not be included in the published pages.
- `remove-cell`
    Not included in the build. Also used by `update_workbook.py` script.

#### Workbook tags
- `solution`:
    Solution of the exercise. Source code will be replaced with a instruction message.
- `remove-cell`:
    Not included in the workbooks. Also used by `jupyter-book`.
- `dmsc-school-hint`:
    Editable cell with hints for students.
    The tagged cell in the workbook will not be read-only,
    unless it is already read-only in the textbook.
- `dmsc-school-keep`:
    Will not be edited or removed. It overwrites all other tags.

## How to update the student notebooks

We keep student notebooks (without solutions) in https://github.com/ess-dmsc-dram/dmsc-school-notebooks.

To update these, navigate to the [Update notebooks](https://github.com/ess-dmsc-dram/dmsc-school-notebooks/actions/workflows/update-notebooks.yml)
section in the Actions tab in that repository and simply run the workflow.

This will create a PR in the notebooks repository with updates to all notebooks.

## Managing dependencies

To add, remove, restrict dependencies, modify `requirements.in` and run
```bash
pip-compile requirements.in
```
to update the dependency pins in `requirements.txt`.
