import psycopg2


def get_conn():
    return psycopg2.connect(host='db',
                           user='postgres',
                           password='1234',
                           database='test',
                           client_encoding='utf-8')


def query_data(sql):
    conn = get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        return cursor.fetchall()
    finally:
        conn.close()


def inser_or_update__data(sql):
    conn = get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
    finally:
        conn.close()