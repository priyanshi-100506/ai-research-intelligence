import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv('DATABASE_URL')

# Strip the SQLAlchemy async driver prefix for the psycopg2 test
if db_url and db_url.startswith('postgresql+asyncpg://'):
    db_url = db_url.replace('postgresql+asyncpg://', 'postgresql://')

try:
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    cur.execute('SELECT 1')
    print('✅ Success: Neon database is reachable.')
    cur.close()
    conn.close()
except Exception as e:
    print(f'❌ Connection failed: {e}')
