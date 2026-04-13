db = db.getSiblingDB("DBMedical");

db.createUser({
  user: "app_user",
  pwd: "securepassword",
  roles: [
    { role: "readWrite", db: "DBMedical" }
  ]
});