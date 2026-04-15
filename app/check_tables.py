from app.database import engine
from sqlalchemy import text

with engine.connect() as conn:

    result = conn.execute(
        text("""
        SELECT table_schema, table_name
        FROM information_schema.tables
        WHERE table_type = 'BASE TABLE'
        ORDER BY table_schema, table_name;
        """)
    )

    for row in result:
        print(row)