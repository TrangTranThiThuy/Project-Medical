# CSV to MongoDB Data Migration Project

## Overview

This project implements a complete data migration pipeline from a CSV file to a MongoDB database. The objective is to ensure a reliable, reproducible, and automated process that validates data integrity, enforces proper typing, removes duplicates, and efficiently loads the dataset into MongoDB.

The solution includes a Python migration script, automated tests, environment management using uv, and full containerization using Docker and Docker Compose.

---

## MongoDB Concepts

This project relies on the following core MongoDB concepts:

* **Database**: A container for collections (e.g., `DBMedical`)
* **Collection**: A group of documents, similar to a table in relational databases (e.g., `Healthcare`)
* **Document**: A JSON-like structure representing a single record

---

## Technologies Used

* Python 3.11
* pandas (data processing)
* pymongo (MongoDB interaction)
* uv (dependency and environment management)
* pytest (automated testing)
* Docker & Docker Compose (containerization)
* MongoDB

---

## Project Structure

```
project/
├── app/
│   └── migrate_csv_to_mongo.py
│   └── test_migration.py
├── data/
│   └── healthcare_dataset.csv
├── pyproject.toml
├── uv.lock
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .ignore
└── README.md
```

---

## Migration Script Logic

The script `migrate_csv_to_mongo.py` performs the following steps:

1. Reads the CSV file using pandas
2. Performs integrity checks:

   * verifies available columns
   * analyzes data types
   * detects missing values
   * identifies duplicates
3. Applies optional type conversion (integer, float, datetime)
4. Removes duplicate rows
5. Converts the dataset into JSON documents
6. Inserts data into MongoDB using batch operations
7. Creates indexes on selected fields for performance optimization
8. Generates JSON reports before and after migration

This approach ensures data consistency and traceability throughout the migration process.

---

## Automated Testing

Automated tests are implemented using pytest to validate:

* CSV structure and content
* data integrity before migration
* successful insertion into MongoDB
* consistency between CSV and database
* absence of null values in critical fields

Tests are executed on a dedicated collection (`Healthcare_test`) to avoid modifying production data.

---

## Using uv

This project uses uv for dependency and environment management.

### Install dependencies

```
uv sync
```

### Run the migration script

```
uv run python migrate_csv_to_mongo.py \
  --csv data/healthcare_dataset.csv \
  --collection Healthcare \
  --db DBMedical
```

### Run tests

```
uv run pytest
```

---

## Docker Deployment

The project is fully containerized using Docker and Docker Compose.

### Start the application

```
docker compose up --build
```

This command will:

* start a MongoDB container
* run the migration script in a separate container
* automatically import the CSV data into the database

---

## Volumes

The following volumes are used:

* `mongo_data`: persists MongoDB data
* `./data`: provides access to the CSV dataset

This ensures data persistence and separation of concerns.

---

## Verifying the Migration

You can verify the data using the MongoDB shell:

```
docker exec -it mongodb mongosh
```

Then run:

```
use DBMedical
db.Healthcare.find().limit(5)
```

Alternatively, you can connect using a GUI tool such as MongoDB Compass.

---

## Key Considerations

* Ensure proper data typing before insertion
* Remove duplicates to maintain data consistency
* Create indexes on frequently queried fields (e.g., Name, Doctor)
* Avoid using the `--drop` option in production environments
* Use test collections when validating migrations

---

## Possible Improvements

* Add schema validation at the MongoDB level
* Implement automatic type detection
* Integrate a web interface (e.g., Mongo Express)
* Extend the pipeline into a full ETL workflow

---

## Conclusion

This project demonstrates a complete and robust approach to data migration from CSV to MongoDB. It integrates best practices in data validation, automation, environment management, and containerization, ensuring a reliable and reproducible workflow suitable for real-world applications.
