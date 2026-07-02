# Python Libraries

In order to promote SciCat adoption and lower the barrier to access and use data and metadata, the SciCat community has worked on creating Python libraries to access the scicat backend endpoint.

There are two SciCat Python libraries, which serve two different use cases:
- Pyscicat ([repository](https://github.com/SciCatProject/pyscicat))  
  ![pySciCat logo](images/pyscicat.png)  
  This is a lower level library providing a Python function for each backend endpoint.  
  The use case for this library is for expert programmers that are developing third-party tools, like ingestors and analysis tools.
  It requires having experience with REST APIs and being familiar with the intricacies of SciCat data models.
  At the time of this writing, Pyscicat is functional but not complete and is lacking some endpoints.  

- Scitacean([repository](https://github.com/SciCatProject/scitacean), [documentation](https://www.scicatproject.org/scitacean/))  
  ![Scitacean logo](images/scitacean.png)  
  This is a high-level library that hides the intricacies of AcpiCat and allows users to access their datasets, associated metadata and files.
  The intended audience for this library are scientist and users that are performing data exploration and are leveraging SciCat to retrieve or store their data.
