import os
import pandas as pd
from pymongo import MongoClient
from migrate_csv_to_mongo import migrate, basic_integrity_checks

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "DBMedical"
SOURCE_COLLECTION = "Healthcare"
TEST_COLLECTION = "Healthcare_test"

CSV_PATH = "data/healthcare_dataset.csv"  # adapte si besoin


def test_existing_data_integrity():
    """
    Vérifie que la collection existante contient des données valides
    """
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    coll = db[SOURCE_COLLECTION]

    count = coll.count_documents({})
    assert count > 0, "La collection Healthcare est vide"

    sample = coll.find_one()

    # Vérifications clés (basées sur ton exemple)
    assert "Name" in sample
    assert "Age" in sample
    assert isinstance(sample["Age"], int)
    assert "Billing Amount" in sample


def test_csv_integrity():
    """
    Vérifie le CSV avant migration
    """
    df = pd.read_csv(CSV_PATH)

    report = basic_integrity_checks(df)

    assert report["n_rows"] > 0
    assert "Name" in report["columns"]
    assert "Age" in report["columns"]


def test_migration_to_test_collection():
    """
    Migration vers une collection TEST (ne touche pas aux vraies données)
    """
    schema = {
        "Age": "int",
        "Billing Amount": "float",
        "Room Number": "int",
        "Date of Admission": "datetime",
        "Discharge Date": "datetime"
    }

    result = migrate(
        csv_path=CSV_PATH,
        mongo_uri=MONGO_URI,
        db_name=DB_NAME,
        collection_name=TEST_COLLECTION,
        schema=schema,
        batch_size=500,
        create_indexes=["Name", "Doctor"],
        drop_before=True  # OK ici car collection test
    )

    assert result["mongo_count"] > 0


def test_data_consistency_between_csv_and_mongo():
    """
    Compare CSV et MongoDB (volume + champs clés)
    """
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    coll = db[TEST_COLLECTION]

    df = pd.read_csv(CSV_PATH)

    mongo_count = coll.count_documents({})
    csv_count = len(df.drop_duplicates())

    # On tolère petite différence (ex: doublons supprimés)
    assert abs(mongo_count - csv_count) < 5

    # Vérifier un document au hasard
    sample = coll.find_one()

    expected_fields = [
        "Name", "Age", "Gender", "Blood Type",
        "Medical Condition", "Doctor", "Hospital"
    ]

    for field in expected_fields:
        assert field in sample


def test_no_null_critical_fields():
    """
    Vérifie qu'il n'y a pas de valeurs nulles sur champs critiques
    """
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    coll = db[TEST_COLLECTION]

    critical_fields = ["Name", "Age", "Doctor"]

    for field in critical_fields:
        count_null = coll.count_documents({field: None})
        assert count_null == 0, f"Valeurs nulles trouvées dans {field}"