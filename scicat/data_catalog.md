# Data Catalog

Generically speaking, a __data catalog__ is a detailed inventory of all data assets in an organization, designed to help data professionals to quickly find the most appropriate data for their purpose. ([1], [2])

A better definition that fits better our use case and, more in general, the world of scientific research in big facilities, is the following:  
### Data catalog
A __data catalog__ is a detailed inventory of all the scientific and experimental data produced at the facility and related to its scientific process, designed and configured to increase data FAIRness, to improve their accessibility and searchability.

In simple words, the data catalog is the place to go in order to search and find data, and gain access to the related data files.

There are many data catalogs available in the software space, some of them open source, some with commercial license. At ESS, we have adopted SciCat which was developed as an in-kind contribution and in collaboration with PSI and MaxIV. It is an open source project, and we are both the project managers and an active contributors.  
The main components of SciCat are:
- the database, which is an instance of mongodb
- the backend, which provides all the data management functionalities and sits on top of the database..
- the frontend, which is a single page application providing a UI to most of the backend functionalities.

More information about SciCat can be found on its [website](https://scicatproject.github.io/), and also the code repositories for the [frontend](https://github.com/SciCatProject/frontend) and [backend](https://github.com/SciCatProject/scicat-backend-next) repositories

------
[1] <https://www.ibm.com/topics/data-catalog> Data Catalog  
[2] <https://www.oracle.com/big-data/data-catalog/what-is-a-data-catalog/> What Is a Data Catalog and Why Do You Need One?  