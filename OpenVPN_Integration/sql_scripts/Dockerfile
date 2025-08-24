FROM mysql:9

# Copy the database creation script
COPY create_db.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/create_db.sh

# Copy the init SQL script to create the schema
COPY initdb.sql /usr/local/bin/

# Set the working directory
WORKDIR /usr/local/bin

# Default command to run the script
CMD ["./create_db.sh"]