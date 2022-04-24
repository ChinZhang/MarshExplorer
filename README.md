# MarshExplorer
Script for loading data extracted from csv files exported from an Zooniverse project, MarshExplorer, into an local MySQL server to collect annotations made by citizen scientists

## Requirements for Running and Management
- [Python](https://www.python.org/downloads/)
- Jupyter notebook (optional if using Python script)
- [MySQL with MySQL Workbench](https://dev.mysql.com/downloads/installer/)

## Overview
1. marsh_explorer.json: can be edited to add any additional subject sets along with any additional subjects of interest that are being annotated by either rectangles or circles
2. MarshExplorer.ipynb: Jupyter notebook file
3. script.py: Python script
4. ER_diagram: image of database schema created in Figma
5. queries.txt: list of requested queries that can be run to query specific data

## Setup
The user is defaulted to root and password to ' '. When setting up the MySQL server, remember your user and password. Then change the code in either the Jupyter file or Python script to update the user and password.
1. Line 7 in the Jupyter notebook file
2. 

## Running the script
1. Make sure the csv file data exports from Zooniverse for classifications and subjects are in the directory. The names should be:
   1. marsh-explorer-classifications.csv
   2. marsh-explorer-subjects.csv
2. Check to see if your MySQL services are on. Go to services.msc and look for MySQL80 and click start
3. Run script
   1. If running on Jupyter notebook, run cell by cell
   2. If running with Python script, run this command in the terminal:


## Managing and Querying the Data
1. Go on MySQL Workbench and connect to the local database.
2. A database called "marshexplorer" should be present on the left list of databases
3. Select the database and click on any tables to view table data
4. Create new SQL tab and copy/paste any queries from the queries.txt file to do specific queries
