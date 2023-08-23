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
```python
dataset_pid = "20.500.12269/761fd17f-e0a8-4bd4-9e70-67ff8647b3f4"
access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiI2MzliMmE1MWI0MTU0OWY1M2RmOWVjMzYiLCJyZWFsbSI6ImxvY2FsaG9zdCIsInVzZXJuYW1lIjoiaW5nZXN0b3IiLCJlbWFpbCI6InNjaWNhdGluZ2VzdG9yQHlvdXIuc2l0ZSIsImVtYWlsVmVyaWZpZWQiOnRydWUsImF1dGhTdHJhdGVneSI6ImxvY2FsIiwiaWQiOiI2MzliMmE1MWI0MTU0OWY1M2RmOWVjMzYiLCJpYXQiOjE2OTIwODc0ODUsImV4cCI6MTY5MjA5MTA4NX0.Phca4UF7WKY367-10Whgwd5jaFjiPku6WsgiPeDh_-o"
```

First of all, you need to import the scitacean library
```python
from scitacean import Client
from scitacean.transfer.ssh import SSHFileTransfer
```

Instantiate the client
```python
sct_client = Client.from_token(
    url=scicat_instance,
    token=token,
    file_transfer=SSHFileTransfer(
        host="login.esss.dk"
    ))
```

than request and retrieve the dataset selected
```python
dset = sct_client.get_dataset("20.500.12269/761fd17f-e0a8-4bd4-9e70-67ff8647b3f4")
```

You can view the dataset information and metadata
```python
dset
```
This command present the following view which show the main information about the dataset.  
![Dataset view in jupyter notebook 1](scitacean_dataset_visualization_collapsed.png)  
  
You can expand the collapsed sections to view the metadata   
  
![Dataset view in jupyter notebook 2](scitacean_dataset_visualization_with_metadata.png) 
  
or the file associated with the dataset.  
  
![Dataset view in jupyter notebook 3](scitacean_dataset_visualization_with_files_list.png)

Once you have verified that the dataset is the correct one, you can download the data files
```python
dset = sct_client.download_files(dset, target="../data", select="60395-2022-02-28_2215.nxs")
dset
```
If we check the files section of the dataset, we can see that the file has been downloaded:  
![Dataset view in jupyter notebook 4](scitacean_dataset_visualization_with_downloaded_files.png)


The current status of the dataset indicates that the first file is available locally with path:
```bash
..\data\60395-2022-02-28_2215.nxs
```

Please note the relative path.
