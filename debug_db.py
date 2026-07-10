import sqlite3
import os

# Adjust this to the path of your actual database file
db_path = "app/database/your_database_name.db" 

def print_db_content():
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        print("--- DEBUG: Scraped Articles ---")
        cursor.execute("SELECT * FROM scraped_article")
        for row in cursor.fetchall():
            print(row)

        print("\n--- DEBUG: Curated Articles ---")
        cursor.execute("SELECT * FROM curated_article")
        for row in cursor.fetchall():
            print(row)

        conn.close()
    except Exception as e:
        print(f"Error accessing database: {e}")

if __name__ == "__main__":
    print_db_content()