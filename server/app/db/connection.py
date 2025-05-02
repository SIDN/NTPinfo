import psycopg2
from config import DB_CONFIG

conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

cur.execute("""
    INSERT INTO times (
        client_sent, client_sent_prec,
        server_recv, server_recv_prec,
        server_sent, server_sent_prec,
        client_recv, client_recv_prec
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    RETURNING id
""", (
    12, 1,  # client_sent
    1714593335001, 223456789,  # server_recv
    1714595001, 323456789,  # server_sent
    1714595001, 423456789   # client_recv
))
measurement_id = cur.fetchone()[0]
print(measurement_id)

conn.commit()
cur.close()
conn.close()


