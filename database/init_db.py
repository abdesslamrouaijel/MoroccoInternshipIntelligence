from database.connection import initialize_database


if __name__ == "__main__":
    initialize_database()
    print("SQLite database initialized.")
