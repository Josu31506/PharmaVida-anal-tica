from flask import Blueprint, jsonify, request
from app.service import analytics_service

analytics_bp = Blueprint("analytics", __name__)

@analytics_bp.route("/ventas", methods=["GET"])
def ventas_por_dia():
    data = analytics_service.ventas_por_dia()
    return jsonify(data)

@analytics_bp.route("/top-productos", methods=["GET"])
def top_productos():
    data = analytics_service.top_productos()
    return jsonify(data)

@analytics_bp.route("/top-usuarios", methods=["GET"])
def top_usuarios():
    data = analytics_service.top_usuarios()
    return jsonify(data)

@analytics_bp.route("/productos-sin-venta", methods=["GET"])
def productos_sin_venta():
    data = analytics_service.productos_sin_venta()
    return jsonify(data)
@analytics_bp.route("/ping", methods=["GET"])
def ping():
    return {"message": "Conectado correctamente con Flask y Athena ✅"}
