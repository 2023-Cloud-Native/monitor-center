print("Starting init the db")
db.getSiblingDB("admin").auth(
  process.env.MONGO_INITDB_ROOT_USERNAME,
  process.env.MONGO_INITDB_ROOT_PASSWORD
);
db.createUser({
  user: process.env.MONGODB_USERNAME,
  pwd: process.env.MONGODB_PASSWORD,
  roles: [{role: "readWrite", "db": process.env.MONGODB_DATABASE}],
});

db = new Mongo().getDB("monitor");
db.createCollection("reservoir", { capped: false });
db.createCollection("electrcity", { capped: false });
db.createCollection("earthquake", { capped: false });
print("Finishing init the db")