from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from common.utils.auth import role_required
from common.utils.enums.roles import Roles
from common.utils.enums.estado_pedido import EstadoPedido
from common.config.db import db
from models import Pedidos, PedidosProductos, Productos, Usuarios

pedidos_user = Blueprint('pedidos_user', __name__)

@pedidos_user.post('/api/usuarios/pedidos')
@jwt_required()
def crear_pedido():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    nuevo_pedido = Pedidos(
        monto_total=data['monto_total'],
        estado_pedido=EstadoPedido.PENDIENTE,
        id_usuarios=current_user_id,
    )
    db.session.add(nuevo_pedido)
    db.session.commit()

    for producto in data['productos']:
        nuevo_producto_pedido = PedidosProductos(
            cantidad=producto['cantidad'],
            cantidad_producto=producto['cantidad_producto'],
            precio=producto['precio'],
            id_pedidos=nuevo_pedido.id_pedidos,
            id=producto['id']
        )
        db.session.add(nuevo_producto_pedido)
    
    db.session.commit()

    return jsonify({"mensaje": "Pedido creado", "id_pedido": nuevo_pedido.id_pedidos}), 201

@pedidos_user.get('/api/usuarios/pedidos/<int:pedido_id>')
@jwt_required()
def obtener_pedido(pedido_id):
    current_user_id = get_jwt_identity()
    pedido = Pedidos.query.filter_by(id_pedidos=pedido_id, id_usuarios=current_user_id).first()
    if not pedido:
        return jsonify({"mensaje": "Pedido no encontrado"}), 404
    
    productos = PedidosProductos.query.filter_by(id_pedidos=pedido_id).all()
    productos_data = [{"id": p.id, "cantidad": p.cantidad, "cantidad_producto": p.cantidad_producto, "precio": p.precio} for p in productos]

    pedido_data = {
        "id_pedido": pedido.id_pedidos,
        "monto_total": pedido.monto_total,
        "estado_pedido": pedido.estado_pedido.value,
        "fecha_creacion": pedido.fecha_creacion,
        "productos": productos_data
    }

    return jsonify(pedido_data), 200

@pedidos_user.get('/api/usuarios/pedidos')
@jwt_required()
def obtener_pedidos_por_usuario():
    current_user_id = get_jwt_identity()
    pedidos = Pedidos.query.filter_by(id_usuarios=current_user_id).all()
    pedidos_data = []
    
    for pedido in pedidos:
        productos = PedidosProductos.query.filter_by(id_pedidos=pedido.id_pedidos).all()
        productos_data = [{"id": p.id, "cantidad": p.cantidad, "precio": p.precio} for p in productos]

        pedidos_data.append({
            "id_pedido": pedido.id_pedidos,
            "monto_total": pedido.monto_total,
            "estado_pedido": pedido.estado_pedido.value,
            "fecha_creacion": pedido.fecha_creacion,
            "productos": productos_data
        })

    return jsonify(pedidos_data), 200

@pedidos_user.patch('/api/usuarios/pedidos/<int:id>')
@jwt_required()
def actualizar_estado_pedido(id):
    current_user_id = get_jwt_identity()
    pedido = Pedidos.query.filter_by(id_pedidos=id, id_usuarios=current_user_id).first_or_404()
    data = request.json
    pedido.estado_pedido = EstadoPedido(data['estado_pedido'])
    db.session.commit()
    return jsonify(message="Estado del pedido actualizado exitosamente")

@pedidos_user.post('/api/usuarios/pedidos/<int:id_pedido>/productos')
@jwt_required()
def agregar_producto_pedido(id_pedido):
    current_user_id = get_jwt_identity()
    pedido = Pedidos.query.filter_by(id_pedidos=id_pedido, id_usuarios=current_user_id).first_or_404()
    data = request.json
    producto = Productos.query.get_or_404(data['id'])
    nuevo_pedido_producto = PedidosProductos(
        cantidad=data['cantidad'],
        cantidad_producto=data['cantidad_producto'],
        precio=producto.precio,
        id_pedidos=id_pedido,
        id=data['id']
    )
    db.session.add(nuevo_pedido_producto)
    pedido.monto_total += float(nuevo_pedido_producto.cantidad) * float(nuevo_pedido_producto.precio)
    db.session.commit()
    return jsonify(message="Producto agregado al pedido exitosamente"), 201

@pedidos_user.get('/api/usuarios/pedidos/<int:pedido_id>/productos')
@jwt_required()
def obtener_productos_pedido(pedido_id):
    current_user_id = get_jwt_identity()
    pedido = Pedidos.query.filter_by(id_pedidos=pedido_id, id_usuarios=current_user_id).first_or_404()
    productos = PedidosProductos.query.filter_by(id_pedidos=pedido_id).all()
    productos_data = [{"id": p.id, 
                       "cantidad": p.cantidad, 
                       "precio": p.precio} for p in productos]

    return jsonify(productos_data), 200

@pedidos_user.delete('/api/usuarios/pedidos/<int:id_pedido>/productos/<int:id_producto>')
@jwt_required()
def eliminar_producto_pedido(id_pedido, id_producto):
    current_user_id = get_jwt_identity()
    pedido = Pedidos.query.filter_by(id_pedidos=id_pedido, id_usuarios=current_user_id).first_or_404()
    pedido_producto = PedidosProductos.query.filter_by(id_pedidos=id_pedido, id=id_producto).first_or_404()
    pedido.monto_total -= float(pedido_producto.cantidad) * float(pedido_producto.precio)
    db.session.delete(pedido_producto)
    db.session.commit()
    return jsonify(message="Producto eliminado del pedido exitosamente")

@pedidos_user.patch('/api/usuarios/pedidos/<int:id_pedido>/productos/<int:id_producto>')
@jwt_required()
def actualizar_cantidad_producto_pedido(id_pedido, id_producto):
    current_user_id = get_jwt_identity()
    pedido = Pedidos.query.filter_by(id_pedidos=id_pedido, id_usuarios=current_user_id).first_or_404()
    pedido_producto = PedidosProductos.query.filter_by(id_pedidos=id_pedido, id=id_producto).first_or_404()
    data = request.json
    nueva_cantidad = data['cantidad']
    
    diferencia_cantidad = float(nueva_cantidad) - float(pedido_producto.cantidad)
    pedido.monto_total += diferencia_cantidad * float(pedido_producto.precio)
    
    pedido_producto.cantidad = nueva_cantidad
    db.session.commit()
    return jsonify(message="Cantidad del producto actualizada exitosamente")


# TRAER TODOS LOS PEDIDOS
@pedidos_user.get('/api/admin/pedidos')
@jwt_required()  # Puedes mantener o quitar la autenticación según lo necesites
@role_required([Roles.ADMIN])
def obtener_todos_pedidos():
    # Obtener todos los pedidos de la base de datos
    pedidos = Pedidos.query.all()
    pedidos_data = []

    for pedido in pedidos:
        productos = PedidosProductos.query.filter_by(id_pedidos=pedido.id_pedidos).all()
        productos_data = [{"id": p.id, "cantidad": p.cantidad, "precio": p.precio} for p in productos]

        pedidos_data.append({
            "id_pedido": pedido.id_pedidos,
            "id_usuario": pedido.id_usuarios,
            "monto_total": pedido.monto_total,
            "estado_pedido": pedido.estado_pedido.value,
            "fecha_creacion": pedido.fecha_creacion,
            "productos": productos_data
        })

    return jsonify(pedidos_data), 200

# TRAER LOS PEDIDOS POR ID
@pedidos_user.get('/api/admin/pedidos/<int:pedido_id>')
@jwt_required()  # Puedes mantener o quitar la autenticación según lo necesites
@role_required([Roles.ADMIN])
def obtener_pedido_por_id(pedido_id):
    # Obtener el pedido por ID sin filtrar por usuario
    pedido = Pedidos.query.get_or_404(pedido_id, description="Pedido no encontrado")
    
    # Obtener los productos asociados al pedido
    productos = PedidosProductos.query.filter_by(id_pedidos=pedido.id_pedidos).all()
    productos_data = [{"id": p.id, "cantidad": p.cantidad, "precio": p.precio} for p in productos]

    # Estructurar la respuesta
    pedido_data = {
        "id_pedido": pedido.id_pedidos,
        "id_usuario": pedido.id_usuarios,
        "monto_total": pedido.monto_total,
        "estado_pedido": pedido.estado_pedido.value,
        "fecha_creacion": pedido.fecha_creacion,
        "productos": productos_data
    }

    return jsonify(pedido_data), 200
