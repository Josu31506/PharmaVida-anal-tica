from flask import Flask
from flask_cors import CORS
from app.controller.analytics_controller import analytics_bp
from dotenv import load_dotenv
from flasgger import Swagger
import os

# Carga las variables del .env
load_dotenv()

app = Flask(__name__)

# Habilitar CORS (para que el frontend pueda hacer requests)
CORS(app)

# Configurar Swagger UI para usar el archivo YAML
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/"
}

# Cargar la documentación desde el archivo YAML
swagger_file_path = os.path.join(os.path.dirname(__file__), 'app', 'docs', 'swagger.yml')

Swagger(app, config=swagger_config, template_file=swagger_file_path)

# Registrar el Blueprint del microservicio analítico
app.register_blueprint(analytics_bp, url_prefix="/api/analitica")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)