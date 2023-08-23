# DMSC School Lecture Materials

## How to export workbook from lecture materials

There is a python script `update_workbook.py` to create a workbook(jupyter notebook) from the jupyter notebook lecture materials.

If a jupyter notebook cell has a `solution` tag, it deletes the sources of the cell and leaves a message instead.

It creates or deletes workbooks from the lecture materials.
And the name of the workbook files are same as the lecture materials.

If there is a python file in the lecture material directories,
it also copies python files into the [workbook submodule](github.com:ess-dmsc-dram/dmsc-school-notebooks).

Once you update the workbook, you have to commit and push the changes of the submodule manually.


```
git submodule update  # Use --init tag if it is the first time pulling submodule
python update_workbook.py --all  # Update all workbooks

# or
python update_workbook.py  # Update based on git status
```

