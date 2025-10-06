from flask import Flask
from flask_cors import CORS
from app.controller.analytics_controller import analytics_bp
from flask import Flask
from dotenv import load_dotenv
from flasgger import Swagger

# 👇 Carga las variables del .env
load_dotenv()

app = Flask(__name__)

# Habilitar CORS (para que el frontend pueda hacer requests)
CORS(app)

# 🔹 Configurar Swagger UI
app.config['SWAGGER'] = {
    'title': 'PharmaVida Analítica API',
    'uiversion': 3
}

# Registrar el Blueprint del microservicio analítico
app.register_blueprint(analytics_bp, url_prefix="/api/analitica")

# Ruta base para verificar que el backend está corriendo
@app.route("/")
def home():
    return {"message": "Microservicio Analítico activo ✅"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)


