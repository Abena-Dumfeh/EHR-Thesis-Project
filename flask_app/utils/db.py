import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="ehruser",
        password="StrongPass2025!",
        database="ehrdb"
    )
