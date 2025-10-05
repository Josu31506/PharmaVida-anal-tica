Backend Analítico – PharmaVida

Microservicio desarrollado en Flask para realizar consultas analíticas sobre datos almacenados en AWS Athena, obtenidos de múltiples fuentes (MySQL, PostgreSQL y MongoDB).
Forma parte del ecosistema de servicios del proyecto PharmaVida, encargado de centralizar reportes de ventas, productos, usuarios y médicos desde una arquitectura distribuida.

📁 Estructura del Proyecto
microservicio-analitico/
├── app/
│   ├── main.py                      # Aplicación principal Flask
│   ├── controller/
│   │   └── analytics_controller.py  # Endpoints de análisis y reportes
│   ├── service/
│   │   └── analytics_service.py     # Lógica de negocio: ejecución de consultas
│   ├── repository/
│   │   └── athena_repository.py     # Conexión y ejecución de queries en AWS Athena
│   ├── domain/                      # (Futuro uso: modelos de dominio)
│   ├── __init__.py                  # Inicialización de paquetes (puede eliminarse)
│
├── .env                             # Variables de entorno locales
├── .env.example                     # Ejemplo de configuración
├── requirements.txt                 # Dependencias del entorno Python
└── README.md                        # Este archivo

⚙️ Funcionalidades

Este microservicio permite realizar consultas analíticas sobre los datos procesados y almacenados en AWS Athena, como:

Ventas por distrito

Top productos más vendidos

Top clientes por gasto

Reporte de productos sin oferta o bajo stock

Consultas SQL personalizadas (en endpoints tipo /query?q=)

🧩 Endpoints Disponibles
1️⃣ Ping / Health Check

GET /api/analitica/ping
Verifica que el backend esté activo y conectado correctamente con AWS Athena.

Respuesta

{ "message": "Conectado correctamente con Flask y Athena ✅" }

2️⃣ Ventas por Distrito

GET /api/analitica/ventas-por-distrito
Devuelve un resumen de las ventas agrupadas por distrito.

Ejemplo de salida

[
  { "distrito": "Ate", "ventas_totales": 1265.50 },
  { "distrito": "Santa Anita", "ventas_totales": 842.30 }
]

3️⃣ Ventas por Producto

GET /api/analitica/ventas-por-producto
Consulta los productos con mayor facturación total.

Consulta ejecutada

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


Ejemplo de respuesta

[
  { "producto_id": 1, "nombre": "Paracetamol 500mg", "total_unidades": 320, "facturacion_total": 1850.00 },
  { "producto_id": 2, "nombre": "Ibuprofeno 400mg", "total_unidades": 210, "facturacion_total": 1320.50 }
]

4️⃣ Top Clientes (Gasto Total)

GET /api/analitica/top-clientes

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

5️⃣ Productos sin oferta activa

GET /api/analitica/productos-sin-oferta

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

6️⃣ Consulta Personalizada

GET /api/analitica/query?q=<consulta>
Permite ejecutar queries SQL personalizadas directamente sobre el catálogo de Athena.

Ejemplo

GET /api/analitica/query?q=SELECT COUNT(*) AS total FROM compras;

⚙️ Configuración
1️⃣ Variables de Entorno

Crear un archivo .env en la raíz del proyecto basado en .env.example:

# AWS Credentials
AWS_ACCESS_KEY_ID=TU_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY=TU_SECRET_ACCESS_KEY
AWS_SESSION_TOKEN=                     # opcional
AWS_REGION=us-east-1

# Athena Configuration
ATHENA_DATABASE=farmacia_ds
ATHENA_OUTPUT_LOCATION=s3://pharmavida-athena-results/

# Flask Config
HOST=0.0.0.0
PORT=5000
DEBUG=True

☁️ Configuración AWS
1️⃣ Requisitos

Bucket S3 existente: pharmavida-athena-results

Configuración de credenciales válida en el entorno:

~/.aws/credentials (si se ejecuta localmente)

Variables de entorno (si se ejecuta en contenedor o EC2)

🧠 Uso
🔹 1. Ejecutar localmente
cd microservicio-analitico
python -m venv venv
source venv/bin/activate    # Linux/Mac
# o
venv\Scripts\activate       # Windows

pip install -r requirements.txt
python app/main.py


El servicio se levantará en:
👉 http://localhost:5000

👉 http://192.168.1.90:5000
 (LAN)

🔹 2. Verificar conexión
curl http://localhost:5000/api/analitica/ping

🔹 3. Consultar endpoints desde frontend (React)

En tu .env del frontend:

VITE_API_ANALITICA=http://192.168.1.90:5000/api/analitica

📊 Ejemplo de Visualización (Frontend React)

El panel AnaliticaDashboard en React consume los endpoints anteriores mediante fetchAnalitica()
para mostrar tablas de resumen de ventas, productos y usuarios, con paginación automática.

🧱 Validaciones y Manejo de Errores

El microservicio maneja errores con mensajes estructurados:

{ "error": "La consulta falló: FAILED" }


Validaciones:
✅ Manejo de errores de conexión a Athena
✅ Respuesta JSON uniforme
✅ CORS habilitado para frontend local (React)
✅ Logging de consultas fallidas

🧰 Requisitos del Sistema

Python 3.10+

Paquetes: Flask, boto3, python-dotenv

Acceso a bucket S3 y permisos en Athena

Archivo .env correctamente configurado
