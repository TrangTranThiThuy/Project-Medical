db = db.getSiblingDB('DBMedical');

db.createUser({
    user: "app_user",
    pwd: "app_password123",
    roles: [
        { role: "readWrite", db: "DBMedical" },
        { role: "dbAdmin", db: "DBMedical" }
    ]
});

db.createCollection("Healthcare");
db.Healthcare.createIndex({ "Name": 1 });
db.Healthcare.createIndex({ "Doctor": 1 });
db.Healthcare.createIndex({ "Hospital": 1 });

print("MongoDB initialization complete: admin and app_user created");
