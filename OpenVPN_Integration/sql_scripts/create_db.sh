#!/bin/bash

# Script to create the guacamole database
echo "Waiting for MySQL server to be ready..."

# Wait for MySQL to be ready
until mysql -h ${MYSQL_HOST:-guacamole-sql} -uroot -p${MYSQL_ROOT_PASSWORD:-pass} -e "SELECT 1" >/dev/null 2>&1; do
    echo "MySQL is not ready yet. Waiting..."
    sleep 2
done

echo "MySQL is ready! Creating guacamole_db..."

# Connect to MySQL and execute the CREATE DATABASE command
mysql -h ${MYSQL_HOST:-guacamole-sql} -uroot -p${MYSQL_ROOT_PASSWORD:-pass} << EOF
CREATE DATABASE IF NOT EXISTS guacamole_db;
SHOW DATABASES;
EOF

if [ $? -eq 0 ]; then
    echo "Database creation completed successfully!"
else
    echo "Error creating database!"
    exit 1
fi

echo "Creating guacamole user and granting permissions..."

# Create user and grant permissions
mysql -h ${MYSQL_HOST:-guacamole-sql} -uroot -p${MYSQL_ROOT_PASSWORD:-pass} << EOF
CREATE USER IF NOT EXISTS 'guacamole_user'@'%' IDENTIFIED BY 'pass';
GRANT SELECT, INSERT, UPDATE, DELETE ON guacamole_db.* TO 'guacamole_user'@'%';
FLUSH PRIVILEGES;
EOF

if [ $? -eq 0 ]; then
    echo "User creation and permissions completed successfully!"
else
    echo "Error creating user or granting permissions!"
    exit 1
fi

echo "Importing SQL data into guacamole_db..."

# Create DB Schema
mysql -h ${MYSQL_HOST:-guacamole-sql} -uroot -p${MYSQL_ROOT_PASSWORD:-pass} guacamole_db < initdb.sql

if [ $? -eq 0 ]; then
    echo "SQL import completed successfully!"
else
    echo "Error importing SQL data!"
    exit 1
fi

echo "Database setup completed successfully!"
