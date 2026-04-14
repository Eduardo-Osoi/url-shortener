# url.py — Acortador de URLs

Proyecto training con **Python 3.12 + FastAPI + SQLite**.  
Sin configuración extra — funciona con solo instalar las dependencias.

---

## Stack

| Capa       | Tecnología              |
|------------|-------------------------|
| API        | FastAPI 0.115            |
| ORM        | SQLAlchemy 2.0           |
| DB         | SQLite (incluido en Python) |
| Validación | Pydantic v2              |
| Servidor   | Uvicorn                  |
| Tests      | pytest                   |

---

## Levantar en VS Code

### 1. Abrir el proyecto
```
Archivo → Abrir carpeta → selecciona /url_shortener
```

### 2. Crear entorno virtual
Abre la terminal integrada (`Ctrl + `` ` ``) y ejecuta:

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Correr el servidor
```bash
python run.py
```

Abre el navegador en: **http://localhost:8000**

---

## Endpoints disponibles

| Método   | Ruta                    | Descripción                   |
|----------|-------------------------|-------------------------------|
| `GET`    | `/`                     | Frontend (UI)                 |
| `GET`    | `/health`               | Health check                  |
| `GET`    | `/r/{slug}`             | Redirección a URL original    |
| `POST`   | `/api/v1/urls`          | Crear URL corta               |
| `GET`    | `/api/v1/urls`          | Listar todas las URLs         |
| `GET`    | `/api/v1/urls/stats`    | Estadísticas globales         |
| `GET`    | `/api/v1/urls/{slug}`   | Detalle de una URL            |
| `DELETE` | `/api/v1/urls/{slug}`   | Eliminar URL (soft delete)    |
| `GET`    | `/docs`                 | Swagger UI (auto-generado)    |

---

## Correr los tests

```bash
pip install pytest httpx
pytest tests/ -v
```

Resultado esperado: **10 tests passed** ✓

---

## Estructura del proyecto

```
url_shortener/
├── app/
│   ├── main.py          ← FastAPI app + rutas especiales
│   ├── database.py      ← Conexión SQLite/PostgreSQL
│   ├── models/
│   │   └── url_model.py ← Modelo SQLAlchemy
│   ├── schemas/
│   │   └── url_schema.py← Pydantic request/response
│   ├── crud/
│   │   └── url_crud.py  ← Operaciones DB
│   └── routers/
│       └── urls.py      ← Endpoints /api/v1/urls
├── static/
│   └── index.html       ← Frontend completo
├── tests/
│   └── test_urls.py     ← 10 tests automatizados
├── run.py               ← Punto de entrada
├── requirements.txt
└── .env.example
```

---

## Variables de entorno (opcionales)

Copia `.env.example` como `.env`:

```bash
cp .env.example .env
```

Por defecto usa SQLite — no necesitas cambiar nada para comenzar.

---

## Próximos pasos (retos)

- [ ] Conectar a PostgreSQL (cambiar `DATABASE_URL` en `.env`)
- [ ] Agregar Redis para cache de redirecciones
- [ ] Implementar autenticación JWT
- [ ] Integrar con Jenkins para CI/CD
- [ ] Agregar métricas con Prometheus + Grafana
