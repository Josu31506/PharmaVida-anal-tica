from app.repository import athena_repository

def ventas_por_dia():
    query = """
        SELECT 
            date_format(date_parse(c.fecha_compra, '%Y-%m-%d %H:%i:%s'), '%Y-%m-%d') AS fecha_dia,
            SUM(cc.cantidad) AS total_unidades,
            SUM(cc.cantidad * p.precio) AS total_monto
        FROM "mysql_compras_csv" c
        JOIN "mysql_compra_productos_csv" cp ON c.id = cp.compra_id
        JOIN "mysql_compra_cantidades_csv" cc ON c.id = cc.compra_id
        JOIN "postgresql_productos_csv" p ON cp.producto_id = p.id
        GROUP BY 1
        ORDER BY 1;
    """
    return athena_repository.ejecutar_en_athena(query)


def top_productos():
    query = """
        SELECT 
            p.id AS producto_id,
            p.nombre,
            SUM(cc.cantidad) AS total_unidades,
            SUM(cc.cantidad * p.precio) AS facturacion_total
        FROM "mysql_compra_productos_csv" cp
        JOIN "mysql_compra_cantidades_csv" cc ON cp.compra_id = cc.compra_id
        JOIN "postgresql_productos_csv" p ON cp.producto_id = p.id
        GROUP BY p.id, p.nombre
        ORDER BY facturacion_total DESC
        LIMIT 10;
    """
    return athena_repository.ejecutar_en_athena(query)


def top_usuarios():
    query = """
        SELECT 
            u.id AS usuario_id,
            u.nombre,
            u.apellido,
            SUM(cc.cantidad * p.precio) AS gasto_total
        FROM "mysql_compras_csv" c
        JOIN "mysql_usuarios_csv" u ON c.usuario_id = u.id
        JOIN "mysql_compra_productos_csv" cp ON c.id = cp.compra_id
        JOIN "mysql_compra_cantidades_csv" cc ON c.id = cc.compra_id
        JOIN "postgresql_productos_csv" p ON cp.producto_id = p.id
        GROUP BY u.id, u.nombre, u.apellido
        ORDER BY gasto_total DESC
        LIMIT 10;
    """
    return athena_repository.ejecutar_en_athena(query)


def productos_sin_venta():
    query = """
        SELECT 
            p.id AS producto_id,
            p.nombre AS nombre_producto,
            p.precio,
            p.stock,
            o.id AS oferta_id,
            o.fecha_vencimiento
        FROM "postgresql_productos_csv" p
        LEFT JOIN "mysql_compra_productos_csv" cp ON p.id = cp.producto_id
        LEFT JOIN "postgresql_ofertas_detalle_csv" od ON p.id = od.producto_id
        LEFT JOIN "postgresql_ofertas_csv" o ON od.oferta_id = o.id
        WHERE cp.producto_id IS NULL
          AND (o.fecha_vencimiento IS NULL OR o.fecha_vencimiento = '')
        ORDER BY p.nombre;
    """
    return athena_repository.ejecutar_en_athena(query)
