from postgres import PostgreSQL
from settings import VKTableName, TGTableName

for table in (VKTableName, TGTableName):
    PostgreSQL().execute_query(f"""
    CREATE TABLE {table.users}(
        user_id INTEGER PRIMARY KEY,
        name TEXT,
        surname TEXT,
        datetime TEXT
    );
    """)

    PostgreSQL().execute_query(f"""
    CREATE TABLE {table.reg_info}(
        user_id INTEGER REFERENCES {table.users}(user_id) UNIQUE,
        user_course TEXT,
        user_group TEXT
    );
    """)

    PostgreSQL().execute_query(f"""
    CREATE TABLE {table.user_status}(
        user_id INTEGER REFERENCES {table.users}(user_id) UNIQUE,
        status TEXT,
        callback TEXT
    );
    """)

    PostgreSQL().execute_query(f"""
    CREATE TABLE {table.messages}(
        message_id INTEGER UNIQUE,
        user_id INTEGER,
        text TEXT,
        datetime TEXT
    );
    """)

    PostgreSQL().execute_query(f"""
    CREATE TABLE {table.ban_list}(
        user_id INTEGER UNIQUE
    );
    """)

    PostgreSQL().execute_query(f"""
    CREATE TABLE IF NOT EXISTS {table.commands}(
        text TEXT UNIQUE,
        answer TEXT
    );
    """)

    PostgreSQL().execute_query(f"""
    CREATE TABLE IF NOT EXISTS {table.custom_answers}(
        user_id INTEGER UNIQUE,
        text TEXT UNIQUE,
        answer TEXT
    );
    """)

    PostgreSQL().execute_query(f"""
    CREATE TABLE IF NOT EXISTS {table.photo_links}(
        text TEXT UNIQUE,
        photo_link TEXT
    );
    """)
