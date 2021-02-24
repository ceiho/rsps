# Research Software - Publication and Sustainability

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/ceiho/rsps/main)

To gain a basic understanding about the publishing behaviour and the sustainability of research software is the objective of this project. The initial step is the identification of research software. Repositories, referencing a research publication or that are referenced by a research publication, are considered as candidates. Currently the scope encompasses repositories that are hosted on GitHub and research publications that are released in the ACM digital library (ACM) or on the arXiv e-print repository (arXiv). In the following steps, the gathered candidates are searched for research software, that is analyzed descriptively afterwards.

## Binder Repository
The Binder repository (https://mybinder.org/v2/gh/ceiho/rsps/main) can be used to reproduce the results with the provided dataset of the following paper:   

Claudia Eitzen and Wilhelm Hasselbring. 2021. Reproducible Sustainability Analysis of Open Research Software Repositories. In WebSci ’21: 13th ACM Conference on Web Science, June 21–25, 2021, Southampton, UK. ACM, New York, NY, USA, 10 pages. https: //doi.org/10.1145/XXXXXXX.XXXXXXX    

The related data are archived on Zenodo (https://doi.org/10.5281/zenodo.4559603). The three analysis notebooks (data_description, classification, and sustainability_analysis) also provide additional analyses. Due to the long runtimes and resource-intensive computations, a more appropriate environment than the Binder repository should be chosen to reproduce the data acquisition, filtering, and classification (acmCrawler, publication_harvester, repository_harvester, and rs_identifier notebooks).

## Prerequisites:
  - Python 3
  - MongoDB  
  - Jupyter Notebook  
  - Packages (see requirements.txt)  
  
## Getting started:  
  - Create a virtual environment  
  - Install required packages (pip install binder/requirements.txt) 
  - Specify parameter in the configuration file  
  - Run the Jupyter Notebooks
  
## Usage
The core elements are the following seven Jupyer Notebooks:
  - acm_crawler
  - publication_harvester
  - repository_harvester
  - rs_identifier
  - data_description
  - classification
  - sustainability_analysis

Between the individual notebooks no data are directly exchanged, instead a shared database is used. The database name and its collections are specified in the configuration file (*database*). If no database is available, the archived dataset (Zenodo) is downloaded. Alternative urls can also be specified (*data_url*). The default parameters are stated in the configuration file. 
  
### Harvesting Data
Repositories hosted on GitHub are harvested with the **repository_harvester** notebook. The search terms (*repo_keywords*), the start (*start_date*) and end (*end_date*) dates of the search period, and the search interval size (*delta*) are specified in the configuration file. When *readme* is not commented out in the *repo_harvester* listing, the README files for the harvested repositories are requested. If a GitHub authentication token is available, it can be specified in the *authentication* list to increase the GitHub REST API rate limits. 

arXiv publications are harvested with the **publication_harvester**. The search terms (*pub_keywords*) are specified in the configuration file.

Whereas arXiv provides an API, the data acquisition of the ACM requires a special handling. Due to the missing API, the ACM website is crawled with the **acm_crawler** notebook. The search terms and search periods are directly defined in the start urls. When executing the crawler, changes on the ACM DL website have to be considered, as well as the blocking of the IP address due to too many calls.

### Filtering Repositories
The **rs_identifier** notebook composes the sets of research software repositories (*rs_repositories*) and research software publications (*rs_publications*). DOI names and shortDOIs are extracted from the harvested repositories. For the repository names, extracted from the harvested publications, the metadata are requested. Research software repository candidates are removed that only consist of Readme, License, and .gitignore files. For the remaining repositories, additional data are requested to compute the sustainability indicators. The research domain of the repositories is determined by harvesting the DOI metadata of the research software publications. Each individual step can be omitted by commenting out the corresponding keyword in the *rsidentifier* list in the configuration file.

### Analyze Data
The **data_description** notebook descripes the general characteristics of the research software repositories. The **classification** notebook classifies the research software repositories according to the All Science Journal Classification (ASJC) of Scopus and the subsamples GitHub, ACM, and arXiv. The **sustainability_analysis** notebook analyzes the research software repositories regarding their sustainability.

## References:
Using MongoDB in Binder (binder and init_db folder): https://github.com/ouseful-template-repos/binder-mongo

  


