echo "** Creating default DB and users"

mysql -u root -p$MYSQL_ROOT_PASSWORD --execute \
    "CREATE DATABASE IF NOT EXISTS $MYSQL_DATABASE;
     CREATE USER IF NOT EXISTS '$MYSQL_USER_NAME'@'%' IDENTIFIED BY '$MYSQL_USER_PASSWORD';
     GRANT ALL PRIVILEGES ON $MYSQL_DATABASE.* TO '$MYSQL_USER_NAME'@'%';
     FLUSH PRIVILEGES;
     DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');"

echo "** Finished creating default DB and users"