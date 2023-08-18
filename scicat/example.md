# Example

This page illustrate the main code sections on how to access the selected dataset from a python jupyter.
The information presented here assumes that you already have performed the following actions:
- logged in in SciCat
- selected the dataset
- copied its pid
- retrieved your access token, using the SciCat frontend. 

Please review the [SciCat page](scicat/scicat) if you need more details on where to find these info. 
Also, we are using the [scitacean python library](scicat/python_libraries).

In addition to he code snippets, we have prepared three jupyter notebooks ready for use which you can adapt to your needs in order to download and upload datasets.
- [access individual dataset]()
- [access multiple datasets]()
- [upload individual dataset]()

## Use case

Let's say that you have performed a seach in SciCat frontend and you have identified a specific dataset that you would like to use for your data analysis.
The two pieces of information that you needs are the dataset pid and the access token, which are the following:
```
dataset_pid = ""
access_token = ""
```

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

