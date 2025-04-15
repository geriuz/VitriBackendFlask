from flask import Blueprint, jsonify, request
from app.common.config.db import db
from app.models.productos import Productos
from app.models import Pedidos, PedidosProductos, Productos, Usuarios

productos_public = Blueprint("productos_public", __name__)

@productos_public.get("/api/publico/productos")
def obtener_productos():
    pedidos_pendientes = db.session.query(PedidosProductos.id, db.func.sum(PedidosProductos.cantidad)).join(Pedidos, PedidosProductos.id_pedidos == Pedidos.id_pedidos).filter(Pedidos.estado_pedido == "PENDIENTE").group_by(PedidosProductos.id).all()
    # print("hola", pedidos_pendientes)
    pendientes_por_producto = {p[0]: p[1] for p in pedidos_pendientes}
    # print("hola 2", pendientes_por_producto)


    productos = Productos.query.all()
    disponibles = []
    for producto in productos:
        cantidad_pedida = pendientes_por_producto.get(producto.id,0)
        disponibles.append({
            "id": producto.id,
            "sku": producto.sku,
            "nombre": producto.nombre,
            "descripcion": producto.descripcion,
            "url_imagen": producto.url_imagen,
            "url_ficha_tecnica": producto.url_ficha_tecnica,
            "unidad_producto": producto.unidad_producto.value,
            "cantidad": producto.cantidad,
            "max_usuario": producto.max_usuario,
            "precio": producto.precio,
            "is_promocion": producto.is_promocion,
            "stock_original": producto.stock,
            "cantidad_pendiente": cantidad_pedida,
            "stock": producto.stock - cantidad_pedida,

            "descuento": producto.descuento,
            "is_activo": producto.is_activo,
            "anunciar": producto.anunciar,
            "id_categorias": producto.id_categorias,
            "id_usuarios": producto.id_usuarios,
            "fecha_inicio_descuento": producto.fecha_inicio_descuento,
            "fecha_fin_descuento": producto.fecha_fin_descuento,
        })
    
    return jsonify(disponibles)

@productos_public.get("/api/publico/productos/<int:id>")
def obtener_producto_por_id(id):
    # Obtener la cantidad pendiente de ese producto
    cantidad_pendiente = db.session.query(
        db.func.sum(PedidosProductos.cantidad)
    ).join(Pedidos, PedidosProductos.id_pedidos == Pedidos.id_pedidos).filter(
        Pedidos.estado_pedido == "PENDIENTE",
        PedidosProductos.id == id
    ).scalar()  # Usamos scalar para obtener un valor único

    # Si no hay pedidos pendientes, la cantidad pendiente es 0
    cantidad_pendiente = cantidad_pendiente or 0

    # Obtener el producto por ID
    producto = Productos.query.get_or_404(id, description='Producto no encontrado')
    if not producto:
        return jsonify({"message": "Producto no encontrado"}), 404

    # Calcular el stock disponible
    stock_disponible = producto.stock - cantidad_pendiente

    # Devolver la información del producto
    return jsonify(
        {
            "id": producto.id,
            "nombre": producto.nombre,
            "descripcion": producto.descripcion,
            "url_imagen": producto.url_imagen,
            "url_ficha_tecnica": producto.url_ficha_tecnica,
            "unidad_producto": producto.unidad_producto.value,
            "cantidad": producto.cantidad,
            "max_usuario": producto.max_usuario,
            "precio": producto.precio,
            "is_promocion": producto.is_promocion,
            "stock_original": producto.stock,
            "cantidad_pendiente": cantidad_pendiente,
            "stock": stock_disponible,
            "descuento": producto.descuento,
            "is_activo": producto.is_activo,
            "anunciar": producto.anunciar,
            "id_categorias": producto.id_categorias,
            "id_usuarios": producto.id_usuarios,
            "fecha_inicio_descuento": producto.fecha_inicio_descuento,
            "fecha_fin_descuento": producto.fecha_fin_descuento,
        }
    )

