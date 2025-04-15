import psycopg2

try:
    conn = psycopg2.connect(
        dbname="jobreccdb",
        user="jobreccdb_owner",
        password="npg_WdFQAET98yhU",
        host="ep-damp-tree-a18ipee2-pooler.ap-southeast-1.aws.neon.tech",
        port=5432,
        sslmode="require",
        # sslrootcert="ap-southeast-1-bundle.pem"
    )
    print("✅ Connection successful!")
    conn.close()
except Exception as e:
    print("❌ Connection failed:", e)