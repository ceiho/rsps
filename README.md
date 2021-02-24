# Research Software - Publication and Sustainability

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/ceiho/rsps/main)

To gain a basic understanding about the publishing behaviour and the sustainability of research software is the objective of this project. The initial step is the identification of research software. Repositories, referencing a research publication or that are referenced by a research publication, are considered as candidates. Currently the scope encompasses repositories that are hosted on GitHub and research publications that are released in the ACM digital library (ACM) or on the arXiv e-print repository (arXiv). In the following steps, the gathered candidates are searched for research software, that is analyzed descriptively afterwards.

The related data are archived on Zenodo, https://doi.org/10.5281/zenodo.4559603.

The three analysis notebooks (data_description, classification, and sustainability_analysis) provide additional analysis for the following paper:
Claudia Eitzen and Wilhelm Hasselbring. 2021. Reproducible Sustainability Analysis of Open Research Software Repositories. In WebSci ’21: 13th ACM Conference on Web Science, June 21–25, 2021, Southampton, UK. ACM, New York, NY, USA, 10 pages. https: //doi.org/10.1145/XXXXXXX.XXXXXXX

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

  


