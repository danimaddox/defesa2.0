import psycopg2

try:
    conexao = psycopg2.connect(
        dbname="postgres",
        user="postgres.ictrkqooqetuxlgrampk",
        password="AuroraClarice@@2025",
        host="aws-1-sa-east-1.pooler.supabase.com",
        port="5432"
    )
    print("✅ Conexão bem-sucedida com o banco de dados!")
    conexao.close()

except Exception as e:
    print("❌ Erro ao conectar:")
    print(e)
