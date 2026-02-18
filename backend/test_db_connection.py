"""
Test database connection to Neon Serverless PostgreSQL.
"""
from app.database.session import get_db_context
from sqlalchemy import text

def test_connection():
    try:
        with get_db_context() as db:
            result = db.exec(text('SELECT 1 as test')).first()
            print('Database connection test: SUCCESS')
            print('Query result:', result)
            return True
    except Exception as e:
        print('Database connection test: FAILED')
        print('Error:', str(e))
        return False

if __name__ == '__main__':
    test_connection()
