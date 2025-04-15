from flask import Blueprint, jsonify
from app.common.config.db import db
from app.models.productos import Productos
from app.models.pedidos_productos import PedidosProductos
from app.models.pedidos import Pedidos
from app.models.usuarios import Usuarios
from sqlalchemy import func
from flask import request
from datetime import datetime, timedelta

admin_stats = Blueprint('admin_stats', __name__, url_prefix='/api/admin/stats')



@admin_stats.route('/productos-mas-vendidos', methods=['GET'])
def productos_mas_vendidos():
    # Obtener el parámetro de periodo (diario, semanal, mensual, anual)
    periodo = request.args.get('periodo', 'mensual')  # Predeterminado: mensual
    fecha_actual = datetime.now()

    # Filtro según el periodo
    if periodo == 'diario':
        fecha_inicio = fecha_actual.date()
    elif periodo == 'semanal':
        fecha_inicio = fecha_actual - timedelta(days=7)
    elif periodo == 'mensual':
        fecha_inicio = fecha_actual.replace(day=1)
    elif periodo == 'anual':
        fecha_inicio = fecha_actual.replace(month=1, day=1)
    else:
        return jsonify({"error": "Periodo no válido"}), 400

    # Consulta con filtro de fecha y límite
    productos_vendidos = db.session.query(
        Productos.nombre,
        func.sum(PedidosProductos.cantidad).label('total_vendido')
    ).join(PedidosProductos, Productos.id == PedidosProductos.id) \
     .join(Pedidos, Pedidos.id_pedidos == PedidosProductos.id_pedidos) \
     .filter(Pedidos.fecha_creacion >= fecha_inicio) \
     .group_by(Productos.nombre) \
     .order_by(func.sum(PedidosProductos.cantidad).desc()) \
     .limit(10) \
     .all()

    # Formatear los datos
    data = [{"producto": producto, "total_vendido": int(total_vendido or 0)}
            for producto, total_vendido in productos_vendidos]

    return jsonify(data)


@admin_stats.route('/ventas-ultimos-6-meses', methods=['GET'])
def ventas_ultimos_6_meses():
    from sqlalchemy import func
    from datetime import datetime, timedelta

    # Obtener la fecha actual y calcular los últimos 6 meses
    fecha_actual = datetime.now()
    fecha_inicio = fecha_actual.replace(day=1) - timedelta(days=30 * 5)  # Hace 6 meses
    formato_fecha = func.date_format(Pedidos.fecha_creacion, '%Y-%m')  # Agrupar por año-mes

    # Consulta para calcular ventas de los últimos 6 meses
    ventas = db.session.query(
        formato_fecha.label('mes'),
        func.sum(Pedidos.monto_total).label('total_ventas')
    ).filter(Pedidos.fecha_creacion >= fecha_inicio) \
     .group_by(formato_fecha) \
     .order_by(formato_fecha) \
     .all()

    # Formatear los datos para la respuesta JSON
    data = [{"mes": mes, "total_ventas": total_ventas} for mes, total_ventas in ventas]
    return jsonify(data)

@admin_stats.route('/ventas-productos-por-fecha', methods=['GET'])
def ventas_productos_por_fecha():
    # Parámetros para el filtro
    limite = int(request.args.get('limite', 10))  # Predeterminado: 10
    fecha_inicio = request.args.get('fecha_inicio', None)
    fecha_fin = request.args.get('fecha_fin', None)

    # Validación de fechas
    if fecha_inicio:
        fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
    if fecha_fin:
        fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d')

    # Construir la consulta
    query = db.session.query(
        Productos.nombre.label("producto"),
        func.date(Pedidos.fecha_creacion).label("fecha"),
        func.sum(PedidosProductos.cantidad * PedidosProductos.precio).label("monto_vendido")
    ).join(PedidosProductos, Productos.id == PedidosProductos.id) \
     .join(Pedidos, Pedidos.id_pedidos == PedidosProductos.id_pedidos)

    # Aplicar filtros de fecha si existen
    if fecha_inicio:
        query = query.filter(Pedidos.fecha_creacion >= fecha_inicio)
    if fecha_fin:
        query = query.filter(Pedidos.fecha_creacion <= fecha_fin)

    # Agrupar, ordenar y limitar los resultados
    ventas = query.group_by(Productos.nombre, func.date(Pedidos.fecha_creacion)) \
                  .order_by(func.sum(PedidosProductos.cantidad * PedidosProductos.precio).desc()) \
                  .limit(limite) \
                  .all()

    # Formatear los datos
    data = [
        {"producto": producto, "fecha": fecha.strftime("%Y-%m-%d"), "monto_vendido": float(monto_vendido)}
        for producto, fecha, monto_vendido in ventas
    ]

    return jsonify(data)


@admin_stats.route('/productos-stock', methods=['GET'])
def productos_stock():
    try:
        productos = db.session.query(Productos.nombre, Productos.stock).all()

        # Procesar los datos
        data = [
            {"producto": producto[0], "stock": producto[1]}
            for producto in productos
        ]
        return jsonify(data)
    except Exception as e:
        return jsonify({"message": f"Error al obtener los datos: {str(e)}"}), 500

# 3. Clientes Más Frecuentes
# Ruta para identificar los clientes que han realizado más pedidos.

@admin_stats.route('/clientes-mas-frecuentes', methods=['GET'])
def clientes_mas_frecuentes():
    clientes_frecuentes = db.session.query(
        Usuarios.nombres,
        func.count(Pedidos.id_pedidos).label('total_pedidos')
    ).join(Pedidos, Usuarios.id_usuarios == Pedidos.id_usuarios) \
     .group_by(Usuarios.nombres) \
     .order_by(func.count(Pedidos.id_pedidos).desc()) \
     .limit(10).all()

    data = [{"cliente": cliente, "total_pedidos": total_pedidos} for cliente, total_pedidos in clientes_frecuentes]
    return jsonify(data)




# 1. Ingresos Totales por Producto
# Ruta para calcular los ingresos generados por cada producto (cantidad vendida × precio).

@admin_stats.route('/ingresos-por-producto', methods=['GET'])
def ingresos_por_producto():
    ingresos = db.session.query(
        Productos.nombre,
        func.sum(PedidosProductos.cantidad * Productos.precio).label('total_ingresos')
    ).join(PedidosProductos, Productos.id == PedidosProductos.id) \
     .group_by(Productos.nombre) \
     .order_by(func.sum(PedidosProductos.cantidad * Productos.precio).desc()) \
     .all()

    data = [{"producto": producto, "total_ingresos": float(total_ingresos)} for producto, total_ingresos in ingresos]
    return jsonify(data)

# 2. Pedidos por Mes
# Ruta para agrupar los pedidos realizados por mes. Esto es útil para analizar tendencias de ventas.

@admin_stats.route('/pedidos-por-mes', methods=['GET'])
def pedidos_por_mes():
    pedidos_mes = db.session.query(
        func.date_format(Pedidos.fecha_creacion, "%Y-%m").label('mes'),
        func.count(Pedidos.id_pedidos).label('total_pedidos')
    ).group_by(func.date_format(Pedidos.fecha_creacion, "%Y-%m")) \
     .order_by('mes') \
     .all()

    data = [{"mes": mes, "total_pedidos": total_pedidos} for mes, total_pedidos in pedidos_mes]
    return jsonify(data)


# 4. Productos con Menor Stock
# Ruta para listar los productos que tienen un stock bajo (menor a un umbral, por ejemplo, 10 unidades).

@admin_stats.route('/productos-con-menor-stock', methods=['GET'])
def productos_con_menor_stock():
    umbral = 10  # Define el umbral para considerar un stock bajo
    productos_bajo_stock = db.session.query(
        Productos.nombre,
        Productos.stock
    ).filter(Productos.stock <= umbral).all()

    data = [{"producto": producto, "stock": stock} for producto, stock in productos_bajo_stock]
    return jsonify(data)

# 5. Categorías Más Vendidas
# Ruta para calcular cuáles categorías tienen más ventas, sumando las cantidades de los productos vendidos por categoría.

@admin_stats.route('/categorias-mas-vendidas', methods=['GET'])
def categorias_mas_vendidas():
    categorias_vendidas = db.session.query(
        Categorias.nombre,
        func.sum(PedidosProductos.cantidad).label('total_vendido')
    ).join(Productos, Categorias.id == Productos.id_categorias) \
     .join(PedidosProductos, Productos.id == PedidosProductos.id) \
     .group_by(Categorias.nombre) \
     .order_by(func.sum(PedidosProductos.cantidad).desc()) \
     .all()

    data = [{"categoria": categoria, "total_vendido": total_vendido} for categoria, total_vendido in categorias_vendidas]
    return jsonify(data)

# 6. Pedidos con Mayores Ventas
# Ruta para listar los pedidos con mayores montos totales.

@admin_stats.route('/pedidos-con-mayores-ventas', methods=['GET'])
def pedidos_con_mayores_ventas():
    pedidos_mayores = db.session.query(
        Pedidos.id_pedidos,
        Pedidos.monto_total,
        Pedidos.fecha_creacion
    ).order_by(Pedidos.monto_total.desc()) \
     .limit(10).all()

    data = [{"id_pedido": id_pedido, "monto_total": float(monto_total), "fecha_creacion": fecha_creacion} for id_pedido, monto_total, fecha_creacion in pedidos_mayores]
    return jsonify(data)

# 7. Stock Actual
# Ruta para devolver el inventario completo de productos, con su stock actual.

@admin_stats.route('/stock-actual', methods=['GET'])
def stock_actual():
    productos_stock = db.session.query(
        Productos.nombre,
        Productos.stock
    ).all()

    data = [{"producto": producto, "stock": stock} for producto, stock in productos_stock]
    return jsonify(data)

# 8. Ventas Totales por Día
# Ruta para calcular las ventas totales (en términos monetarios) agrupadas por día.

@admin_stats.route('/ventas-por-dia', methods=['GET'])
def ventas_por_dia():
    ventas_dia = db.session.query(
        func.date(Pedidos.fecha_creacion).label('dia'),
        func.sum(Pedidos.monto_total).label('total_ventas')
    ).group_by(func.date(Pedidos.fecha_creacion)) \
     .order_by('dia') \
     .all()

    data = [{"dia": str(dia), "total_ventas": float(total_ventas)} for dia, total_ventas in ventas_dia]
    return jsonify(data)