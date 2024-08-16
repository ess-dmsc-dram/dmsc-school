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

## Jupyter notebooks
Many of materials are written in notebooks and are published online by `jupyter-book`.
Here are some tips and tools for writing jupyter notebooks for courses.

### Clearing output
Command to clear outputs of all jupyter notebooks in the current directory.
```bash
tree -ifF -P *.ipynb | grep .ipynb | xargs -n1 jupyter nbconvert --ClearOutputPreprocessor.enabled=True --inplace
```

### Building the book

Make sure you have installed all the dependencies in the `requirements.txt` file.
Then use (from the root folder):

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

## How to export workbook from lecture materials

There is a python script `update_workbook.py` to create a workbook(jupyter notebook)
from the jupyter notebook lecture materials in [course directories](#Course-Directories)
based on the [tags](#Workbook-tags) of each cells.

All cells in the workbook will be read-only by default except for `solution` cells.
Cells can be tagged with `dmsc-shool-hint` to keep their editability.

If there is python files, or image files('*.png', '*.jpg', '*.svg') in the lecture material directories,
it also copies them into the [workbook submodule](github.com:ess-dmsc-dram/dmsc-school-notebooks).

It doesn't handle other type of files on purpose.

### 1. Set up or update submodule:workbooks
You need to set up the git submodule `workbooks` before you run the script.

```bash
git -C workbooks branch # Make sure if you're in the right branch of submodule

git submodule update  # Use --init tag if it is the first time pulling submodule
```

### 2. Update workbooks
And then you can update materials.
```bash
python update_workbook.py --all  # Update all workbooks

# or
python update_workbook.py  # Update based on git status
```

### 3. Commit & push workbooks
Once you update the workbook,
you have to commit and push the changes of the submodule manually.

The script will report which files are updated based on `git status`.

The script doesn't commit any changes automatically on purpose
to avoid unexpected changes of workbooks.
