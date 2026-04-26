// Switches to the database
db = db.getSiblingDB('DBMedical');
// Creates app_user
db.createUser({
    user: process.env.MONGO_APP_USER,
    pwd: process.env.MONGO_APP_PASSWORD,
    // Grants readWrite and dbAdmin roles on DBMedical
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
