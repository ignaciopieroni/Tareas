import psycopg2, sys

try:
    conn = psycopg2.connect(
        dbname='tasks_db',
        user='backend_drf',
        password='1234',
        host='localhost',
        port=5432
    )
    print('OK: connected to tasks_db as backend_drf')
    conn.close()
except Exception as e:
    print('ERROR connecting to Postgres:')
    print(e)
    sys.exit(1)
