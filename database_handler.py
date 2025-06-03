import psycopg2
from psycopg2 import sql
from psycopg2.errors import UndefinedTable
from constants import FacebookDataTable
from config import Config
from uuid import uuid4

class PostgresDBHandler:
    def __init__(self):
        self.conn = None
        self.cursor = None

    def connect(self):
        try:
            self.conn = psycopg2.connect(
                dbname=Config.database_name,
                user=Config.database_user,
                password=Config.database_password,
                host=Config.database_host,
                port=Config.database_port
            )
            self.cursor = self.conn.cursor()
        except Exception as e:
            print(f"Database connection failed: {e}")

    def ensure_table_exists(self):
        create_query = f"""
        CREATE TABLE IF NOT EXISTS {FacebookDataTable.table_name.value} (
            User_ID UUID PRIMARY KEY,
            Review_Name TEXT,
            Review_Text TEXT
        );
        """
        try:
            self.cursor.execute(create_query)
            self.conn.commit()
        except Exception as e:
            print(f"Error ensuring table exists: {e}")
            self.conn.rollback()

    def insert_review(self, review_data_list: list):
        print("Inserting The Review Data into database.")
        insert_query = sql.SQL(f"""
        INSERT INTO {FacebookDataTable.table_name.value} (User_ID, Review_Name, Review_Text)
        VALUES (%s, %s, %s)
        ON CONFLICT (User_ID) DO NOTHING;
        """)
        try:
            for review_data in review_data_list:
                self.cursor.execute(
                    insert_query,
                    (
                        review_data["user id"],
                        review_data["review by"],
                        review_data["comment"]
                    )
                )
                self.conn.commit()
                print("Inserted review successfully.")
        except Exception as e:
            print(f"Error inserting review data: {e}")
            self.conn.rollback()

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()


### Example Usage ...
if __name__ == "__main__":
    scraped_data = {
        "User_ID": str(uuid4()),
        "Review_Name": "John Doe",
        "Review_Text": "Great service!"
    }

    # Initialize handler
    db_handler = PostgresDBHandler()
    db_handler.connect()
    db_handler.ensure_table_exists()  # ✅ This was missing
    db_handler.insert_review(scraped_data)
    db_handler.close()
