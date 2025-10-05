# 🧠 Microservicio Analítico – PharmaVida

Backend desarrollado en **Flask (Python)** para ejecutar **consultas analíticas sobre AWS Athena**, obteniendo datos procesados desde múltiples fuentes (MySQL, PostgreSQL y MongoDB) previamente cargadas en **S3 mediante AWS Glue**.
Este servicio actúa como el **motor de analítica** del ecosistema *PharmaVida*, conectado al frontend “Athena Analytics”.

---

## 💽 Estructura del Proyecto

```
microservicio-analitico/
├── app/
│   ├── controller/
│   │   └── analytics_controller.py     # Rutas y endpoints del microservicio
│   ├── domain/                         # (Reservado para lógica de negocio)
│   ├── repository/
│   │   └── athena_repository.py        # Conexión y ejecución de queries en Athena
│   └── service/
│       └── analytics_service.py        # Capa intermedia entre controlador y Athena
├── .env                                # Variables de entorno (no subir)
├── .env.example                        # Ejemplo de configuración segura
├── requirements.txt                    # Dependencias Python
├── main.py                             # Punto de entrada Flask
└── README.md                           # Este archivo
```

---

## ⚙️ Funcionalidades Principales

| Endpoint                             | Método | Descripción                                              |
| ------------------------------------ | ------ | -------------------------------------------------------- |
| `/api/analitica/ping`                | GET    | Verifica la conexión con Flask y AWS Athena              |
| `/api/analitica/query?q=<SQL>`       | GET    | Ejecuta una consulta SQL personalizada en Athena         |
| `/api/analitica/ventas-por-distrito` | GET    | Consulta agregada: ventas totales agrupadas por distrito |
| `/api/analitica/ventas-por-producto` | GET    | Top 10 de productos más vendidos                         |

---

## ☁️ Flujo General

```
Frontend (Athena Dashboard)
        ↓
Flask API (microservicio analítico)
        ↓
AWS Athena (SQL Serverless)
        ↓
S3 Bucket con resultados
```

Cada consulta es enviada a Athena → ejecutada sobre el **catálogo Glue definido en el entorno** →
y los resultados son devueltos al frontend en formato JSON.

---

## 🧩 Configuración del Entorno

### 1️⃣ Variables de entorno (`.env`)

Crea un archivo `.env` en la raíz del proyecto (basado en `.env.example`):

```bash
# ==============================
# ☁️ CONFIGURACIÓN AWS
# ==============================
AWS_ACCESS_KEY_ID=TU_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY=TU_SECRET_ACCESS_KEY
AWS_SESSION_TOKEN=               # Opcional (para sesiones temporales)
AWS_REGION=us-east-1

# ==============================
# 🧠 CONFIGURACIÓN ATHENA
# ==============================
ATHENA_DATABASE=farmacia_ds                  # Nombre del catálogo Glue
ATHENA_OUTPUT_LOCATION=s3://pharmavida-athena-results/
ATHENA_WORKGROUP=primary                     # (opcional)
```

> ⚠️ **Importante:**
>
> * No incluyas este archivo en Git (`.env` debe estar en `.gitignore`)
> * Asegúrate de tener permisos de ejecución sobre Athena y escritura sobre el bucket S3.

---

## 🚀 Ejecución del Proyecto

### ▶️ En entorno local (desarrollo)

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate    # (Linux/Mac)
venv\Scripts\activate       # (Windows)

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar el servidor Flask
python main.py
```

El backend quedará disponible en:

```
http://localhost:5000/api/analitica
```

---

### ▶️ Ejemplo de uso con `curl`

#### Verificar conexión

```bash
curl http://localhost:5000/api/analitica/ping
```

#### Consultar ventas por distrito

```bash
curl http://localhost:5000/api/analitica/ventas-por-distrito
```

#### Ejecutar query personalizada

```bash
curl "http://localhost:5000/api/analitica/query?q=SELECT * FROM mysql_compras_csv LIMIT 5"
```

---

## 📊 Consultas Implementadas

### 1️⃣ Ventas diarias

```sql
SELECT 
    date_format(date_parse(c.fecha_compra, '%Y-%m-%d %H:%i:%s'), '%Y-%m-%d') AS fecha_dia,
    SUM(cc.cantidad) AS total_unidades,
    SUM(cc.cantidad * p.precio) AS total_monto
FROM compras c
JOIN compra_productos cp ON c.id = cp.compra_id
JOIN compra_cantidades cc ON c.id = cc.compra_id
JOIN productos p ON cp.producto_id = p.id
GROUP BY 1
ORDER BY 1;
```

### 2️⃣ Top 10 productos más vendidos

```sql
SELECT 
    p.id AS producto_id,
    p.nombre,
    SUM(cc.cantidad) AS total_unidades,
    SUM(cc.cantidad * p.precio) AS facturacion_total
FROM compra_productos cp
JOIN compra_cantidades cc ON cp.compra_id = cc.compra_id
JOIN productos p ON cp.producto_id = p.id
GROUP BY p.id, p.nombre
ORDER BY facturacion_total DESC
LIMIT 10;
```

### 3️⃣ Usuarios con mayor gasto

```sql
SELECT 
    u.id AS usuario_id,
    u.nombre,
    u.apellido,
    SUM(cc.cantidad * p.precio) AS gasto_total
FROM compras c
JOIN usuarios u ON c.usuario_id = u.id
JOIN compra_productos cp ON c.id = cp.compra_id
JOIN compra_cantidades cc ON c.id = cc.compra_id
JOIN productos p ON cp.producto_id = p.id
GROUP BY u.id, u.nombre, u.apellido
ORDER BY gasto_total DESC
LIMIT 10;
```

### 4️⃣ Productos sin venta ni oferta

```sql
SELECT 
    p.id AS producto_id,
    p.nombre AS nombre_producto,
    p.precio,
    p.stock,
    o.id AS oferta_id,
    o.fecha_vencimiento
FROM productos p
LEFT JOIN compra_productos cp ON p.id = cp.producto_id
LEFT JOIN ofertas_detalle od ON p.id = od.producto_id
LEFT JOIN ofertas o ON od.oferta_id = o.id
WHERE cp.producto_id IS NULL
  AND (o.fecha_vencimiento IS NULL OR o.fecha_vencimiento = '')
ORDER BY p.nombre;
```

---

## 🧬 Estructura de Respuesta JSON

Ejemplo de retorno de Athena:

```json
[
  { "distrito": "Huaycán", "ventas_totales": 5234.50 },
  { "distrito": "Ate", "ventas_totales": 3900.75 }
]
```

---

## 🔧 Requisitos del Sistema

* Python 3.11+
* AWS CLI configurado
* Credenciales válidas de AWS (Athena, S3, Glue)
* Acceso al bucket de resultados definido en `.env`

---

## 🛡️ Seguridad

* ✅ No se exponen credenciales en el repositorio
* ✅ `.env` y `~/.aws/credentials` deben mantenerse privados
* ✅ Peticiones HTTPS recomendadas en despliegue
* ✅ Configuración modular: AWS, Flask y Athena gestionados por variables de entorno

---

## 🛠️ Troubleshooting

| Problema                               | Solución                                                                       |
| -------------------------------------- | ------------------------------------------------------------------------------ |
| **Error: `La consulta falló: FAILED`** | Verifica que las tablas en Glue tengan datos y delimitadores correctos.        |
| **Error de credenciales AWS**          | Asegúrate de haber configurado `~/.aws/credentials` y `.env` correctamente.    |
| **Bucket inexistente o sin permisos**  | Crea el bucket y asigna permisos de lectura/escritura.                         |
| **Flask no conecta con frontend**      | Asegúrate de habilitar CORS (`flask_cors.CORS(app)`) y usar IP local correcta. |

---

## 📘 Autor

**PharmaVida Data Team**
Desarrollado por el equipo de Ingeniería de Datos y Backend de *PharmaVida*
🧠 Integrado con el ecosistema **Athena Analytics Dashboard**.
