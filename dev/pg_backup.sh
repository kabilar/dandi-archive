#!/bin/bash

# Database credentials
HOST="ec2-35-168-130-158.compute-1.amazonaws.com"
PORT="5432"
USER="u8cfndphbguhq8"
DBNAME="dcq75eotjue787"

# Get list of tables excluding those that start with "django"
TABLES=$(psql -h $HOST -p $PORT -U $USER -d $DBNAME -t -c "SELECT tablename FROM pg_tables WHERE schemaname = 'public' AND tablename NOT LIKE 'django%';")

# Backup data of each table
for TABLE in $TABLES; do
    pg_dump -a -h $HOST -p $PORT -U $USER -t $TABLE $DBNAME >> backup.sql
done
