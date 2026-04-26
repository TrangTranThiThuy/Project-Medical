#!/usr/bin/env python3
"""
migrate_csv_to_mongo.py

Usage:
  - Create a .env file containing MONGO_URI and MONGO_DB and (optionally) CSV_PATH
  - python migrate_csv_to_mongo.py --csv healthcare_dataset.csv --collection Healthcare
"""

import os
import argparse
import logging
from dotenv import load_dotenv
import pandas as pd
from pymongo import MongoClient, errors
from pymongo.errors import BulkWriteError
from tqdm import tqdm
import json
from jsonschema import validate, ValidationError
import glob

# ------------------------
# Logging configuration
# ------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# ------------------------
# Load .env
# ------------------------
#load_dotenv()  # reads variables from a .env file and sets them in os.environ # lit .env if exists
DEFAULT_MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DEFAULT_DB = os.getenv("MONGO_DB", "test")

# ------------------------
# Functions
# ------------------------
def detect_and_convert_types(df: pd.DataFrame, 
                            schema: dict = None) -> pd.DataFrame:
    """
    Supported types: int, float, bool, str, datetime
    """
    from pandas.api.types import is_numeric_dtype, is_datetime64_any_dtype

    casts = {'int': 'Int64', 'float': 'float', 'bool': 'boolean', 'str': 'string', 'datetime': 'datetime64[ns]','double': 'float', 'objectId':'string'}
    if schema:
        for col, t in schema.items():
            if col not in df.columns:
                logger.warning("Expected column '%s' missing from CSV.", col)
                continue
            try:
                target = casts.get(t)
                if not target:
                    logger.warning("Target type unknown '%s' for %s", t, col)
                    continue
                if t == "datetime":
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                else:
                    df[col] = df[col].astype(target, errors='ignore')
            except Exception as e:
                logger.warning("Impossible to cast %s in %s : %s", col, t, e)
    return df

def basic_integrity_checks(df: pd.DataFrame):
    """
    Returns a dictionary containing test results: columns, types, duplicates, missing values
    """
    report = {}
    report['n_rows'] = len(df)
    report['n_columns'] = len(df.columns)
    report['columns'] = list(df.columns)
    report['dtypes'] = df.dtypes.apply(lambda x: str(x)).to_dict()
    report['n_duplicates'] = int(df.duplicated().sum())
    report['missing_per_column'] = df.isna().sum().to_dict()
    # types summary
    report['sample_types'] = {
        col: str(type(df[col].dropna().iloc[0]).__name__) 
        if df[col].dropna().shape[0]>0 
        else 'empty' 
        for col in df.columns
    }
    return report

def dataframe_to_mongo_docs(df: pd.DataFrame):
    """
    Convert a pandas DataFrame to JSON documents (native types) 
    - Replace numpy types with native python types if needed
    """
    records = df.where(pd.notnull(df), None).to_dict(orient='records')
    return records

# ------------------------
# Migration
# ------------------------
def migrate(csv_path: str, 
            mongo_uri: str, 
            db_name: str, 
            collection_name: str,
            schema: dict = None, 
            batch_size: int = 1000, 
            create_indexes: list = None, 
            drop_before: bool = False):
    logger.info("Reading the CSV: %s", csv_path)
    df = pd.read_csv(csv_path)
    logger.info("CSV read: %d rows, %d columns", df.shape[0], df.shape[1])

    # Tests before migration
    logger.info("Executing integrity tests before migration...")
    pre_report = basic_integrity_checks(df)
    logger.info("Before migration - rows: %d, duplicates: %d", pre_report['n_rows'], pre_report['n_duplicates'])

    # Schema application
    if schema:
        logger.info("Application of the scheme for type conversion...")
        df = detect_and_convert_types(df, schema)

    # Basic deduplication (columns can be configured)
    if pre_report['n_duplicates'] > 0:
        logger.info("Removing %d duplicates (by identical lines)...", pre_report['n_duplicates'])
        df = df.drop_duplicates()

    # Report after cleaning
    post_report = basic_integrity_checks(df)
    logger.info("After cleaning - rows: %d, duplicates: %d", post_report['n_rows'], post_report['n_duplicates'])

    # MongoDB Connection
    logger.info("Connecting to MongoDB (%s) ...", mongo_uri)
    client = MongoClient(mongo_uri)
    db = client[db_name]
    coll = db[collection_name]

    if drop_before:
        logger.warning("drop_before True => removing the collection %s.%s", db_name, collection_name)
        coll.drop()

    # Creating relevant indexes
    if create_indexes:
        for idx in create_indexes:
            # idx can be either a field or a list of tuples [(field, direction)]
            logger.info("Creating index: %s", idx)
            try:
                if isinstance(idx, str):
                    coll.create_index([(idx, 1)])
                elif isinstance(idx, (list, tuple)):
                    coll.create_index(idx)
                else:
                    logger.warning("Format index non reconnu: %s", idx)
            except errors.PyMongoError as e:
                logger.error("Erreur création index %s : %s", idx, e)

    # Prepare the documents
    docs = dataframe_to_mongo_docs(df)
    logger.info("Sending documents to MongoDB (%d docs)...", len(docs))

    # Batch insert
    # Inserts large CSV data in smaller batches to avoid memory or write-size issues.
    # Provides progress feedback.
    # Handles partial failures gracefully instead of stopping on the first bad document.
    inserted = 0
    try:
        for i in tqdm(range(0, len(docs), batch_size), desc="Insertion batches"):
            batch = docs[i:i+batch_size]
            if not batch:
                continue
            result = coll.insert_many(batch, ordered=False)
            inserted += len(result.inserted_ids)
    except BulkWriteError as bwe:
        logger.error("Bulk write error : %s", bwe.details)
        # count successful
        inserted = coll.count_documents({})
    except Exception as e:
        logger.exception("Error during insertion: %s", e)
        inserted = coll.count_documents({})

    logger.info("Insertion completed. Documents inserted (approx) : %d", inserted)

    # Simple post-migration tests
    post_count = coll.count_documents({})
    logger.info("Documents in MongoDB (%s.%s) : %d", db_name, collection_name, post_count)

    # Exporting reports to local JSON files (traceability)
    os.makedirs("json", exist_ok=True)
    base_name = os.path.splitext(os.path.basename(csv_path))[0]
    # Delete old report files for this CSV
    old_pre = glob.glob(f"json/{base_name}_pre_report.json")
    old_post = glob.glob(f"json/{base_name}_post_report.json")
    for f in old_pre + old_post:
        os.remove(f)
        logger.info("Deleted old report: %s", f)
    with open(f"json/{base_name}_pre_report.json", "w", encoding="utf-8") as f:
        json.dump(pre_report, f, ensure_ascii=False, indent=2)
    with open(f"json/{base_name}_post_report.json", "w", encoding="utf-8") as f:
        json.dump(post_report, f, ensure_ascii=False, indent=2)

    logger.info("Rapports pré/post migration sauvegardés: json/%s_pre_report.json, json/%s_post_report.json", base_name, base_name)

    return {
        "inserted_estimate": inserted,
        "mongo_count": post_count,
        "pre_report": pre_report,
        "post_report": post_report
    }

# ------------------------
# CLI
# ------------------------
def parse_args():
    p = argparse.ArgumentParser(description="Migrate CSV to MongoDB with integrity checks")
    p.add_argument("--csv", default="data/healthcare_dataset.csv", help="CSV file path")
    p.add_argument("--collection", default="Healthcare", help="Name of the target MongoDB collection")
    p.add_argument("--db", default=DEFAULT_DB, help="Name of the target MongoDB database")
    p.add_argument("--uri", default=DEFAULT_MONGO_URI, help="MongoDB URI (e.g., mongodb://localhost:27017)")
    p.add_argument("--batch", type=int, default=1000, help="Size of batches for insert_many")
    p.add_argument("--drop", action="store_true", help="Drop the target collection before inserting")
    p.add_argument("--indexes", nargs="*", help="List of fields to index (space-separated)")
    p.add_argument("--schema", help="JSON file path for schema definition (col: type) to enforce typing")
    return p.parse_args()

def load_schema(path):
    import json
    if not path:
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

if __name__ == "__main__":
    args = parse_args()
    schema = load_schema(args.schema)
    indexes = args.indexes if args.indexes else None

    result = migrate(
        csv_path=args.csv,
        mongo_uri=args.uri,
        db_name=args.db,
        collection_name=args.collection,
        schema=schema,
        batch_size=args.batch,
        create_indexes=indexes,
        drop_before=args.drop
    )
    logger.info("Migration result: %s", result)