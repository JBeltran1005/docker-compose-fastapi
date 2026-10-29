import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor
import redis
from fastapi import FastAPI, Response, status
from pydantic import BaseModel

app = FastAPI(title="Users API with Compose")

# Lectura de variables de entorno
DB_USER = os.getenv("POSTGRES_USER", "appuser")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "appsecret")
DB_NAME = os.getenv("POSTGRES_DB", "usersdb")
DB_HOST = os.getenv("POSTGRES_HOST", "postgres")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

# Cliente de Redis
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)

class UserCreate(BaseModel):
    name: str
    email: str

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )

@app.on_event("startup")
def startup():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

# CAMBIO VISIBLE EN LA RESPUESTA PARA EL PASO 10
@app.get("/health")
def health():
    return {"status": "ok", "service": "api", "version": "v1.1"}

@app.post("/users", status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        "INSERT INTO users (name, email) VALUES (%s, %s) RETURNING id, name, email;",
        (user.name, user.email)
    )
    new_user = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    
    # Invalidar caché en Redis al crear un nuevo registro
    r.delete("users_list")
    return new_user

@app.get("/users")
def get_users(response: Response):
    # 1. Verificar si existe en caché de Redis
    cached_users = r.get("users_list")
    if cached_users:
        response.headers["X-Cache"] = "HIT"
        return json.loads(cached_users)

    # 2. Si no está en caché (MISS), consultar en PostgreSQL
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT id, name, email FROM users ORDER BY id ASC;")
    users = cur.fetchall()
    cur.close()
    conn.close()

    # Guardar en Redis temporalmente (expira en 60 segundos)
    r.setex("users_list", 60, json.dumps(users))
    response.headers["X-Cache"] = "MISS"
    return users
