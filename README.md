# MarshExplorer
Script for loading data extracted from csv files exported from an Zooniverse project, MarshExplorer, into an local MySQL server to collect annotations made by citizen scientists for salt marsh photos

** These notes are for Windows, commands may differ for Mac

## Overview
1. marsh_explorer.json: can be edited to add any additional subject sets along with any additional subjects of interest that are being annotated by either rectangles or circles
2. MarshExplorer.ipynb: Jupyter notebook file
3. script.py: Python script
4. ER_diagram: image of database schema created in Figma
5. queries.txt: list of requested queries that can be run to query specific data

## Installment Requirements
- [Python](https://www.python.org/downloads/)
- Jupyter notebook (optional if using Python script)
- [MySQL with MySQL Workbench](https://dev.mysql.com/downloads/installer/)

1. When setting up MySQL, take note of your database username and password

## Setup for Python script
1. Navigate into the folder after pulling repo and open the command line
2. In the command line, run to install the dependencies for PyMySQL:
> $ python -m pip install PyMySQL
3. Download the csv files from Zooniverse for classifications and subjects and put them in the directory. The names should be:
- marsh-explorer-classifications.csv
- marsh-explorer-subjects.csv

## Running the Python Script
1. Check to see if your MySQL services are on. Go to services.msc and look for MySQL80 and click start
2. Run script
   1. Run this command in the terminal to run Python script:
   > $ python script.py
3. Enter your username and password from setting up MySQL in the command line

## Managing and Querying the Data
1. Go on MySQL Workbench and connect to the local database.
2. A database called "marshexplorer" should be present on the left list of databases
3. Select the database and click on any tables to view table data
4. Create new SQL tab and copy/paste any queries from the queries.txt file to do specific queries

## Editing JSON File
File needs to be edited when:
1. New subject sets are added on Zooniverse
- Follow format and add the subject set id (assigned in Zooniverse), subject set name and location
3. New subjects of interest are added on Zooniverse
- Follow format and add the name of subjects of interest under the corresponding shape
4. New shapes for annotating are added on Zooniverse
- Follow format and add the shape along with any subjects of interest being annotated by it
- **Note: code and database needs to be changed to account for any new tool labels (shapes) for annotation