# WDB Mini-Challenge LO4

## Overview
This Github-Repo was created in order to collect all files necessary for the Mini-Challenge treating all contents of LO4 of Web Data Collection (WDB). The Repo Contains a web scraper, which scrapes job ads from the webpage www.jobscout24.ch
using the Python-Package "Selenium". Furthermore, it contains a test-file to test different features of the scraper and an R-Project to treat the resulting data from the scraping process and create graphs for the final report.

## Goal of Project
Economics of labour market are very important for several decision makers, i.e. federal government, parliament, job centers, central bank etc. However, information about labour market often lags days or even months behind, which leads to
delayed labour market or economic interventions by decision makers. As job ads usually represent an up do date situation of labour markets, one can get updatet data 24/7 from job ad portals such as "Jobscout 24" in Switzerland. The web scraper
developped during this project presents an interesting tool for data collection, which then can be used by policy-makers.

## Structure
The Repo is structured as follows:
- Datasets
  - gemeindestand.xlsx (List of municipalities, obtained from the swiss federal office for statistics)
  - jobscout24_all_jobs.csv (Data from last scraping process. For Up-to-date data, please run respective .py-script)
- workflows
  - python_tests.yml (Automatically runs tests on main web scraper file when changes are pushed to repo)
- wdb_mc_scraper.py (Main Web scraper file to scrape job ad data from www.jobscout24.ch)
- test_scraper.py (Test file to test different features of wdb_mc_scraper.py)
- wdb_mc_eda.R (R-Script to perform baic explorative data analysis on the data obtained by wdb_mc_scraper.py)
- wdb_mc.Rproj (Git-Framework for R-File used do perform EDA)
- requirements.txt (Packages required for Python-scripts)

## Author
This project was conducted by Pascal Trösch (FHNW Data Science).

## Acknowledgements

Bundesamt für Statistik (2025): Gemeindestand (https://www.agvchapp.bfs.admin.ch/de/state/results?SnapshotDate=06.04.2025) [Obtained from website 21.11.2025]


