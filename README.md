# 1. Project Overview

This project transfers data from a CSV file into a MongoDB database.
It demonstrates the use of NoSQL concepts and Python scripting for automated data migration.

# 2. Prerequisites

- Python 3.x installed
- MongoDB installed locally
- Virtual environment (recommended)
- Required Python modules (see requirements.txt)

# 3. MongoDB Concepts

- Document: A JSON-like record representing a single entry in the database.
- Collection: A group of documents.
- Database: A container for collections.

# 4. Script Logic

The migration script performs the following steps:

1. Reads data from <CSV_FILE_NAME>.csv.
2. Validates the data:
 - Checks for missing values and duplicates
 - Transforms the data if necessary.
3. Ensures correct data types
4. Inserts the cleaned data into the MongoDB collection <COLLECTION_NAME> in the database <DB_NAME>.