"""
Check current database schema state.
"""
from app.database.session import get_db_context
from sqlalchemy import text

def check_tables():
    print("=== Checking Database Tables ===")
    with get_db_context() as db:
        result = db.exec(text("""
            SELECT tablename
            FROM pg_tables
            WHERE schemaname = 'public'
            ORDER BY tablename
        """)).all()

        print(f"\nExisting tables ({len(result)}):")
        for table in result:
            print(f"  - {table[0]}")
    return result

def check_indexes():
    print("\n=== Checking Database Indexes ===")
    with get_db_context() as db:
        result = db.exec(text("""
            SELECT
                tablename,
                indexname,
                indexdef
            FROM pg_indexes
            WHERE schemaname = 'public'
            ORDER BY tablename, indexname
        """)).all()

        print(f"\nExisting indexes ({len(result)}):")
        current_table = None
        for idx in result:
            if idx[0] != current_table:
                current_table = idx[0]
                print(f"\n  {current_table}:")
            print(f"    - {idx[1]}")
    return result

def check_foreign_keys():
    print("\n=== Checking Foreign Key Constraints ===")
    with get_db_context() as db:
        result = db.exec(text("""
            SELECT
                tc.table_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name,
                tc.constraint_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
                AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
                AND tc.table_schema = 'public'
            ORDER BY tc.table_name, kcu.column_name
        """)).all()

        print(f"\nExisting foreign keys ({len(result)}):")
        current_table = None
        for fk in result:
            if fk[0] != current_table:
                current_table = fk[0]
                print(f"\n  {current_table}:")
            print(f"    - {fk[1]} -> {fk[2]}.{fk[3]} ({fk[4]})")
    return result

if __name__ == '__main__':
    try:
        check_tables()
        check_indexes()
        check_foreign_keys()
        print("\n=== Database Schema Check Complete ===")
    except Exception as e:
        print(f"\nError: {e}")
