# Laboratorio: Contenerización de una API FastAPI con Dockerfile y Docker Compose

**Estudiante:** Juan Beltran  
**Tecnologías:** Docker, Docker Compose, FastAPI, PostgreSQL, Redis, Python  

---

## 1. Descripción del Proyecto y Arquitectura

Este proyecto contiene una arquitectura multicontenedor orquestada mediante Docker Compose, compuesta por tres servicios interconectados a través de una red interna:

* **api (FastAPI):** Servicio backend para crear y consultar usuarios mediante endpoints REST (`/health` y `/users`). Publica el puerto `8000` en el host.
* **postgres (PostgreSQL 15 Alpine):** Base de datos relacional para el almacenamiento persistente de los usuarios mediante un volumen administrado (`postgres_data`).
* **redis (Redis 7 Alpine):** Almacén en memoria utilizado como capa de caché temporal para la consulta de usuarios, con invalidación automática al registrar nuevos registros.

---

## 2. Requisitos Previos

* Docker Engine
* Docker Compose v2

---

## 3. Configuración de Variables de Entorno

La aplicación lee su configuración desde variables de entorno. Para ejecutar el proyecto localmente:

1. Copiar la plantilla de ejemplo:
   cp .env.example .env

2. Variables configuradas en `.env`:
   * `POSTGRES_USER`: Usuario de la base de datos (`appuser`).
   * `POSTGRES_PASSWORD`: Contraseña de la base de datos (`appsecret`).
   * `POSTGRES_DB`: Nombre de la base de datos (`usersdb`).
   * `POSTGRES_PORT`: Puerto interno de conexión (`5432`).
   * `POSTGRES_HOST`: Nombre del servicio Compose (`postgres`).
   * `REDIS_HOST`: Nombre del servicio Compose (`redis`).
   * `REDIS_PORT`: Puerto del servicio Redis (`6379`).
   * `API_PORT`: Puerto expuesto en el host (`8000`).

*(Nota: El archivo `.env` se encuentra excluido del repositorio mediante `.gitignore` para proteger las credenciales).*

---

## 4. Construcción y Ejecución

### 4.1. Construcción individual de la imagen (Punto 3)
```bash
docker build -t juan/users-api:v1 .
docker image ls
