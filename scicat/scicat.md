# SciCat

SciCat is the data catalog of choiche in ESS.  
It has been developed as in-kind contribution and through a collaboration between ESS, [PSI](https://www.psi.ch/en) and [MaxIV](https://www.maxiv.lu.se/).  

Current version is _4.x_, and it is based on the following technologies:
- backend
  - mongodb
  - mongoose
  - typescript
  - node.js
  - nest.js
- frontend
  - node.js
  - angular.js

In order to log in into SciCat, please click on the user icon visible on the top right corner of any page. You will see the login screen

![SciCat Datasets List](images/scicat_login.png)

Once you have successfully logged in, you are directed to the dataset list page.  
  
![SciCat Datasets List](images/scicat_datasets_list.png)

This page includes the search form which provides all the functionalities to search and find a specific subset of datasets.  
Using the search form you can select the datasets that are of your interests. You can view the details page of a specific dataset (show below) by clicking on it.

![SciCat Dataset List](images/scicat_dataset_details.png)

If you need to use the access token in other applications, you can find it under the _settings_ item of the _main menu_ accessible by clicking on the user icon on the top right corner of the page. 
The access token, also called authentication token, is visible under the name __SciCat Token__. As you can see, the UI offers a convenient _copy to clipboard_ functionality.

![SciCat User Settings](images/scicat_user_settings.png)
