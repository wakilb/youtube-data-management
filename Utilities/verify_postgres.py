import psycopg

try:
    conn = psycopg.connect(
        dbname="youtube_data",
        user="postgres",  
        password="your_postgres_password",
        host="localhost", 
        port=5432
    )
    cursor = conn.cursor()
    cursor.execute("SELECT 1;") 
    result = cursor.fetchone()
    print("PostgreSQL connection successful! Test query result:", result)
    conn.close()

except Exception as e:
    print("PostgreSQL connection failed:", e)
