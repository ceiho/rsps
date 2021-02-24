# Research Software - Publication and Sustainability

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/ceiho/rsps/main)

To gain a basic understanding about the publishing behaviour and the sustainability of research software is the objective of this project. The initial step is the identification of research software. Repositories, referencing a research publication or that are referenced by a research publication, are considered as candidates. Currently the scope encompasses repositories that are hosted on GitHub and research publications that are released in the ACM digital library (ACM) or on the arXiv e-print repository (arXiv). In the following steps, the gathered candidates are searched for research software, that is analyzed descriptively afterwards.

The related data are archived on Zenodo, https://doi.org/10.5281/zenodo.4559603.

The Binder repository (https://mybinder.org/v2/gh/ceiho/rsps/main) can be used to reproduce the results with the provided dataset of the following paper:   

Claudia Eitzen and Wilhelm Hasselbring. 2021. Reproducible Sustainability Analysis of Open Research Software Repositories. In WebSci ’21: 13th ACM Conference on Web Science, June 21–25, 2021, Southampton, UK. ACM, New York, NY, USA, 10 pages. https: //doi.org/10.1145/XXXXXXX.XXXXXXX    

The three analysis notebooks (data_description, classification, and sustainability_analysis) also provide additional analyses. Due to the long runtimes and resource-intensive computations, a more appropriate environment than the Binder repository should be chosen to reproduce the data acquisition, filtering, and classification (acmCrawler, publication_harvester, repository_harvester, and rs_identifier notebooks).


## Prerequisites:
  - Python 3
  - MongoDB  
  - Jupyter Notebook  
  - Packages (see binder/requirements.txt)  
  
## Getting started:  
  - Create a virtual environment  
  - Install required packages (pip install binder/requirements.txt) 
  - Specify parameter in the configuration file  
  - Run the Jupyter Notebooks

## References:
  - Using MongoDB in Binder (binder and init_db folder): https://github.com/ouseful-template-repos/binder-mongo

  


