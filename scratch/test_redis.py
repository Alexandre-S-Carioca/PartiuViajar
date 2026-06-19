import redis
from flight_engine.core.config import settings

def test_connection():
    print(f"Tentando se conectar ao Redis em: {settings.REDIS_URL}...")
    try:
        r = redis.Redis.from_url(settings.REDIS_URL, socket_connect_timeout=5)
        response = r.ping()
        if response:
            print("✅ Conectado com sucesso ao Redis no servidor 192.168.0.150!")
        else:
            print("❌ O Redis respondeu, mas não retornou PING com sucesso.")
    except Exception as e:
        print(f"❌ Falha ao se conectar ao Redis: {e}")

if __name__ == "__main__":
    test_connection()
