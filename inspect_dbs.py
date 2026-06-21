import sqlite3, os

for db_path in [
    r'C:\Users\AR CALHAU\source\repos\LotoScope\lotofacil_lite\lotofacil.db',
    r'C:\Users\AR CALHAU\source\repos\LotoScope\lotofacil_lite\lotoscope_aprendizado.db',
    r'C:\Users\AR CALHAU\source\repos\LotoScope\LotoScope.db'
]:
    name = os.path.basename(db_path)
    print('=' * 60)
    print(f'DATABASE: {name}')
    print(f'Path: {db_path}')
    print(f'Exists: {os.path.exists(db_path)}')
    print(f'Size: {os.path.getsize(db_path) if os.path.exists(db_path) else 0} bytes')
    print()
    
    if not os.path.exists(db_path):
        continue
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        print(f'TABLES ({len(tables)}):')
        for t in tables:
            print(f'  - {t[0]}')
        print()
        
        for t in tables:
            table_name = t[0]
            cursor.execute(f'PRAGMA table_info("{table_name}")')
            columns = cursor.fetchall()
            print(f'  TABLE: {table_name}')
            print(f'  COLUMNS ({len(columns)}):')
            for col in columns:
                print(f'    {col[0]:3d}. {col[1]:25s} {col[2]:15s} {"NOT NULL" if col[3] else "NULLABLE":10s} default={col[4]}')
            cursor.execute(f'SELECT COUNT(*) FROM "{table_name}"')
            count = cursor.fetchone()[0]
            print(f'  ROWS: {count:,}')
            if count > 0:
                cursor.execute(f'SELECT * FROM "{table_name}" LIMIT 2')
                rows = cursor.fetchall()
                print(f'  SAMPLE:')
                for row in rows:
                    print(f'    {row}')
            print()
        conn.close()
    except Exception as e:
        print(f'  ERROR: {e}')
    print()
