import os
import mysql.connector


class MySQLConnector:
    def __init__(self):
        self._user = 'root'
        self._password = os.getenv('MYSQL_PASSWORD')
        self._host = 'localhost'
        self._database = 'twitter'
        self._cnx = None
        self._cursor = None

    def get_server_connection(self):
        try:
            self._cnx = mysql.connector.connect(
                user=self._user,
                password=self._password,
                host=self._host,
                database=self._database
            )
            print("Connection successful")
        except mysql.connector.Error as err:
            print(f"Error while connecting to MySQL server: {err}")

    def execute_query(self, query, values=None):
        try:
            with self._cnx.cursor() as cursor:
                cursor.execute(query, values or ())
                if query.strip().lower().startswith('select'):
                    return cursor.fetchall()  # Fetch all results
                self._cnx.commit()
        except mysql.connector.Error as err:
            print(f"Error executing query: {err}")


    def _commit_changes(self):
        self._cnx.commit()

    def close_server_connection(self):
        self._cursor.close()
        self._cnx.close()
