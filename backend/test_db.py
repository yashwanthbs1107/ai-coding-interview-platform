import psycopg

conn = psycopg.connect(
    host="localhost",
    port=5433,
    dbname="ai_coding_platform",
    user="postgres",
    password=""
)

print("Database connected!")

difficulty="Easy"
cursor=conn.cursor()
cursor.execute("SELECT * from problems WHERE difficulty=%s;",
               (difficulty,))

rows=cursor.fetchall()
print(rows)

conn.close()