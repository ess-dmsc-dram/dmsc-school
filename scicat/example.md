# Example

In this page illustrate an example on how to access the selected dataset from a python jupyter.
The information presented here assumes that you already have selected the dataset and copied its pid, together with save your accee token, using the SciCat frontend. Please see the [SciCat page](scicat/scicat) if you need more details on where to find these info. 
Also, we are using the [scitacean python library](scicat/python_libraries).

We prepared three jupyter notebooks ready for use which you can adapt to download and upload datasets.
- [access individual dataset]()
- [access multiple datasets]()
- [upload individual dataset]()

Following is snippets of the code contained in the two notebooks and, can also be found in scitacean documentation.

First of all, you need to import the scitacean library
```python
```

Instantiate the client
```python
```

than request and retrieve the dataset selected
```python
```

You can view the dataset information and metadata
```python
```

Once you have verified that the dataset is the correct one, you can download the data files
```python
```

