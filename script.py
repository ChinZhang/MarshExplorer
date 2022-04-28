import pymysql
pymysql.install_as_MySQLdb()
import MySQLdb
import pandas as pd
import json

# Reading in csv files and storing them into data frames using pandas
classifications_df = pd.read_csv('marsh-explorer-classifications.csv')
subjects_df = pd.read_csv('marsh-explorer-subjects.csv')


# Cleaning the sql file to be executed
def parse_sql(filename):
    data = open(filename, 'r').readlines()
    statements = []
    DELIMITER = ';'
    statement = ''

    for lineno, line in enumerate(data):
        if not line.strip():
            continue

        if line.startswith('--'):
            continue

        if 'DELIMITER' in line:
            DELIMITER = line.split()[1]
            continue

        if DELIMITER not in line:
            statement += line.replace(DELIMITER, ';')
            continue

        if statement:
            statement += line
            statements.append(statement.strip())
            statement = ''
        else:
            statements.append(line.strip())
    return statements


# Inserting users into user table
def users_table(cursor):
    users_sql = "INSERT INTO user (user_id, username, expert) VALUES (%s, %s, %s)"

    # Set initial expert status to false (0)
    expert = 0

    # Loop through the classification dataframe that has the csv file
    for row in classifications_df.itertuples():

        # Get all user ids from database
        cursor.execute("SELECT user_id FROM user where user_id=%s", row.user_id)
        user_data = cursor.fetchall()

        # Check if the user is already in database
        if not user_data:
            # If the expert value is true from csv data
            if row.expert == "TRUE":
                # Set expert status to true (1)
                expert = 1

            # Insert the data into the database
            cursor.execute(users_sql, (row.user_id, row.user_name, expert))
        else:
            continue


# Inserting workflows into workflow table
def workflows_table(cursor):
    workflows_sql = "INSERT INTO workflow (workflow_id, workflow_name) VALUES (%s, %s)"

    # Loop through the classification dataframe that has the csv file
    for row in classifications_df.itertuples():

        # Get all workflow ids from database
        cursor.execute("SELECT workflow_id FROM workflow where workflow_id=%s", row.workflow_id)
        workflow_data = cursor.fetchall()

        # Check if the workflow is already in database
        if not workflow_data:
            # Insert the data into the database
            cursor.execute(workflows_sql, (row.workflow_id, row.workflow_name))
        else:
            continue


# Inserting subject into subject table
def subjects_table(cursor):
    subjects_sql = "INSERT INTO subject (subject_id, image_path, height, width) VALUES (%s, %s, %s, %s)"
    image_path = ""
    height = 0
    width = 0

    # Loop through the classification dataframe that has the csv file
    for row in classifications_df.itertuples():
        # Get all subject ids from database
        cursor.execute("SELECT subject_id FROM subject where subject_id=%s", row.subject_ids)
        subject_data = cursor.fetchall()

        # Check if the subject is already in database
        if not subject_data:
            # Load in json and parse it down to filename
            load_subject_data = json.loads(row.subject_data)
            subject_id_data = load_subject_data[str(row.subject_ids)]
            image_path = subject_id_data['Filename']

            # Insert the data into the database
            cursor.execute(subjects_sql, (row.subject_ids, image_path, height, width))
        else:
            continue


# Inserting classifications into classification table
def classifications_table(cursor):
    classifications_sql = "INSERT INTO classification (classification_id, workflow_id, user_id, date, gold_standard, workflow_version) VALUES (%s, %s, %s, %s, %s, %s)"

    # Sett initial gold standard status to false (0)
    gold_standard = 0

    # Insert annotations into annotations, circles and rectangles table
    annotations_sql = "INSERT INTO annotation (annotation_id, subject_id, classification_id) VALUES (%s, %s, %s)"
    circles_sql = "INSERT INTO circle (circle_id, annotation_id, tool_label, radius, x, y, angle) VALUES (null, %s, %s, %s, %s, %s, %s)"
    rectangles_sql = "INSERT INTO rectangle (rectangle_id, annotation_id, tool_label, x, y, width, height) VALUES (null, %s, %s, %s, %s, %s, %s)"

    # Initialize annotation_id
    annotation_id = 0

    # Alter Table SQL is only needed if auto_increment needs to be reset to 1 in database
    cursor.execute("ALTER TABLE annotation AUTO_INCREMENT = 1")
    cursor.execute("ALTER TABLE circle AUTO_INCREMENT = 1")
    cursor.execute("ALTER TABLE rectangle AUTO_INCREMENT = 1")

    # Get the max annotation id from annotation table
    cursor.execute("SELECT max(annotation_id) from annotation")
    max_annotation_id = cursor.fetchone()

    # Start the annotation id at 1 if there is nothing is database
    if max_annotation_id[0] is None:
        annotation_id = 1
    else:
        # Add one to the current max annotation id
        annotation_id = max_annotation_id[0] + 1

    # Open and load json file for tool labels
    marsh_explorer_json = open('marsh_explorer.json')
    marsh_explorer_data = json.load(marsh_explorer_json)

    # Loop through the classification dataframe that has the csv file
    for row in classifications_df.itertuples():

        # Get all classification ids from database
        cursor.execute("SELECT classification_id FROM classification where classification_id=%s", row.classification_id)
        classification_data = cursor.fetchall()

        # Check if the classification is already in database
        if not classification_data:

            # If the gold standard status is true from csv data
            if row.gold_standard == "TRUE":
                # Set gold standard status to true (1)
                gold_standard = 1

            # Insert the classification data into database
            cursor.execute(classifications_sql, (
                row.classification_id, row.workflow_id, row.user_id, row.created_at, gold_standard,
                row.workflow_version))

            # Load in json for annotation data
            load_annotation_data = json.loads(row.annotations)

            # Disable foreign key constraint to allow insertion of data for annotations
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

            # Insert annotation data into the annotations table from csv file
            cursor.execute(annotations_sql, (annotation_id, row.subject_ids, row.classification_id))

            # Loop through the data from the loaded json data that was from the csv file
            for data in load_annotation_data:
                # Get the values of value from the data
                for value in data['value']:

                    # Loop through the marsh explorer json to get tool labels
                    for tool_label in marsh_explorer_data['tool_labels']:

                        # Rectangles Table
                        # Loop to get all the names of subject of interests that uses rectangle annotation
                        for name in tool_label['rectangle']:
                            # If tool label is equal to json names of interest then insert data into rectangles table
                            if value['tool_label'] == str(name['name']):
                                cursor.execute(rectangles_sql, (
                                    annotation_id, value['tool_label'], value['x'], value['y'], value['width'],
                                    value['height']))

                        # Circles Table
                        # Loop to get all the names of subject of interests that uses circle annotation
                        for name in tool_label['circle']:
                            # If tool label is equal to json names of interest then insert data into circles table
                            if value['tool_label'] == str(name['name']):
                                cursor.execute(circles_sql, (
                                    annotation_id, value['tool_label'], value['r'], value['x'], value['y'],
                                    value['angle']))

            # Increment annotation id
            annotation_id = annotation_id + 1

        else:
            continue


# Updating subject set location information
def subject_set_info(cursor):
    subject_set_sql = "UPDATE subject SET subject_set_id=%s, subject_set_name=%s, location=%s WHERE subject_id=%s"

    # Open and load json file for subject sets
    marsh_explorer_json = open('marsh_explorer.json')
    marsh_explorer_data = json.load(marsh_explorer_json)

    subject_set_name = "0"
    location = "0"
    # Loop through the dataframe that has the csv file
    for row in subjects_df.itertuples():

        # Get all subject ids from database
        cursor.execute("SELECT subject_id FROM subject where subject_id=%s", row.subject_id)
        subject_data = cursor.fetchall()

        # Set subject set name and location based on the subject set id
        if subject_data:

            # Loop through marsh explorer json to get the subject sets
            for subject_set in marsh_explorer_data['subject_sets']:
                # if the subject set id from csv is equal to the json data subject id, set location and subject set name
                if row.subject_set_id == int(subject_set['subject_set_id']):
                    subject_set_name = subject_set['subject_set_name']
                    location = subject_set['location']

            cursor.execute(subject_set_sql, (row.subject_set_id, subject_set_name, location, row.subject_id))

        else:
            continue


# Ask user for database username and password
user = input("Enter your username: ")
password = input("Enter your password: ")

# Connect to the database
connection = MySQLdb.connect(host='localhost', user=user, password=password)

# Use cursor to execute SQL queries for the database
cursor = connection.cursor()

# Checking if marshexplorer database already exists
cursor.execute("SHOW DATABASES LIKE 'marshexplorer'")
res = cursor.fetchone()

# Execute sql file if it exists
if res is None:
    # Read sql statements from sql file and execute
    statements = parse_sql('marshexplorer.sql')
    for statement in statements:
        cursor.execute(statement)

    connection.commit()
else:
    cursor.execute("USE marshexplorer")

# Call other functions to populate table and commit
users_table(cursor)
workflows_table(cursor)
subjects_table(cursor)
classifications_table(cursor)
subject_set_info(cursor)

connection.commit()
