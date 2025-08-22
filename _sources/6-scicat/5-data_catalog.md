# Data Catalog

Generically speaking, a __data catalog__ is a detailed inventory of all data assets available in an organization, designed to help data professionals to quickly find the most appropriate data for their purpose. ([1], [2])

A better definition that fits our use case and, more in general, the world of scientific research in big facilities, is the following:

## Data catalog
A __data catalog__ is the tool that allows for a detailed inventory of all the scientific and experimental data produced at the facility and related to its scientific process. It is designed and configured to increase data FAIRness, to improve findability, accessibility, interoperability and reusability.

In simple words, the data catalog is the place to go in order to search and find data, and gain access to the related data files.

There are many data catalogs available in the software space, some of them open source, some under commercial license.
At ESS, we have adopted __SciCat__ which was developed as an in-kind contribution and in collaboration with PSI and MaxIV.
It is an open source project, and we are both the project leaders and active contributors.  
The main components of SciCat are:
- The database, which is an instance of mongodb.
- The backend, which provides all the data management functionalities and connects to the database.
- The frontend, which is a single page web application providing a UI to most of the backend functionalities.

More information about SciCat can be found on its [website](https://www.scicatproject.org/), and also the code repositories for the [frontend](https://github.com/SciCatProject/frontend) and [backend](https://github.com/SciCatProject/scicat-backend-next) repositories

------
[1] <https://www.ibm.com/think/topics/data-catalog> Data Catalog  
[2] <https://www.oracle.com/big-data/data-catalog/what-is-a-data-catalog/> What Is a Data Catalog and Why Do You Need One?  
