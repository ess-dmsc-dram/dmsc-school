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
    Not included in the build. Also used by `strip_solutions.py` script.

#### Workbook tags
- `solution`:
    Solution of the exercise. Source code will be replaced with an instruction message.
- `remove-cell`:
    Not included in the workbooks. Also used by `jupyter-book`.
- `dmsc-school-keep`:
    Will not be edited or removed. It overwrites all other tags.

>We used to have workbooks ``read-only`` to make ``git pull`` easier
whenever we want to update the workbooks without making any conflicts with students' work. </br>
But now they are stable and it is very little likely to pull more changes during the school so we decided not to make them read-only. </br>
So, if you want to make any cells read-only in the workbook, it should be applied in the metadata manually.

## How to export student notebooks from lecture materials

There is a python script `strip_solutions.py` to create a student notebooks
from the jupyter notebook lecture materials in [course directories](##Course-Directories).

The notebooks will be copies of the originals, with the solutions stripped out
(replaced by cells that read "Add your solution here").

Start from the root folder of the `dmsc-school` repo.

We first strip the outputs from all notebooks.
```bash
tree -ifF -P *.ipynb | grep .ipynb | xargs -n1 jupyter nbconvert --ClearOutputPreprocessor.enabled=True --inplace
```

Then clone the notebooks repo and clear it out:
```bash
git clone git@github.com:ess-dmsc-dram/dmsc-school-notebooks.git
rm -r dmsc-school-notebooks/*
```

Then run the script to strip the solutions, pointing to the `dmsc-school-notebooks` folder for output:
```bash
python strip_solutions.py dmsc-school-notebooks
```

Finally, push the notebooks to the remote (and open a pull request):
```bash
cd dmsc-school-notebooks
git checkout -b <MY_UPDATE_BRANCH>
git add -A .
git push origin <MY_UPDATE_BRANCH>
```
