from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.common.utils.auth import role_required
from app.common.utils.enums.roles import Roles
from app.common.utils.enums.estado_pedido import EstadoPedido
from app.common.config.db import db
from app.models import Pedidos, PedidosProductos, Productos, Usuarios

pedidos_user = Blueprint('pedidos_user', __name__)

@pedidos_user.post('/api/usuarios/pedidos')
@jwt_required()
def crear_pedido():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    nuevo_pedido = Pedidos(
        monto_total=data['monto_total'],
        direccion=data['direccion'],
        forma_entrega=data['forma_entrega'],
        barrio=data['barrio'],
        ciudad=data['ciudad'],
        estado_pedido=EstadoPedido.PENDIENTE,
        id_usuarios=current_user_id,
    )
    db.session.add(nuevo_pedido)
    db.session.commit()

    for producto in data['productos']:
        nuevo_producto_pedido = PedidosProductos(
            cantidad=producto['cantidad'],
            cantidad_producto=producto['cantidad_producto'],
            nombre_producto=producto['nombre_producto'],
            unidad_producto=producto['unidad_producto'],
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
    productos_data = [{"id": p.id, "cantidad": p.cantidad, "cantidad_producto": p.cantidad_producto, "precio": p.precio, "nombre_producto":p.nombre_producto, "unidad_producto":p.unidad_producto} for p in productos]


    # Acceder al nombre y apellido del usuario relacionado
    nombre_usuario = pedido.usuarios.nombres if pedido.usuarios else None
    apellido_usuario = pedido.usuarios.apellidos if pedido.usuarios else None
    identificacion_usuario = pedido.usuarios.identificacion if pedido.usuarios else None

    pedido_data = {
        "id_pedido": pedido.id_pedidos,
        "nombre_usuario": nombre_usuario,  # Agregar el nombre del usuario
        "apellido_usuario": apellido_usuario,  # Agregar el apellido del usuario
        "identificacion_usuario": identificacion_usuario,  # Agregar la identificacion del usuario
        "monto_total": pedido.monto_total,
        "direccion": pedido.direccion,
        "forma_entrega": pedido.forma_entrega,
        "barrio": pedido.barrio,
        "ciudad": pedido.ciudad,
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
        productos_data = [{"id": p.id, "cantidad": p.cantidad, "cantidad_producto": p.cantidad_producto, "precio": p.precio, "nombre_producto":p.nombre_producto, "unidad_producto":p.unidad_producto} for p in productos]

        # Acceder al nombre y apellido del usuario relacionado
        nombre_usuario = pedido.usuarios.nombres if pedido.usuarios else None
        apellido_usuario = pedido.usuarios.apellidos if pedido.usuarios else None
        identificacion_usuario = pedido.usuarios.identificacion if pedido.usuarios else None
        
        pedidos_data.append({
            "id_pedido": pedido.id_pedidos,
            "nombre_usuario": nombre_usuario,  # Agregar el nombre del usuario
            "apellido_usuario": apellido_usuario,  # Agregar el apellido del usuario
            "identificacion_usuario": identificacion_usuario,  # Agregar la identificacion del usuario
            "monto_total": pedido.monto_total,
            "direccion": pedido.direccion,
            "forma_entrega": pedido.forma_entrega,
            "barrio": pedido.barrio,
            "ciudad": pedido.ciudad,
            "estado_pedido": pedido.estado_pedido.value,
            "fecha_creacion": pedido.fecha_creacion,
            "productos": productos_data
            })

    return jsonify(pedidos_data), 200

@pedidos_user.patch('/api/usuarios/pedidos/<int:id>')
@jwt_required()  # Requiere autenticación JWT
@role_required([Roles.ADMIN])  # Solo permite acceso a usuarios con el rol ADMIN
def actualizar_estado_pedido(id):
    # Buscar el pedido por su ID
    pedido = Pedidos.query.filter_by(id_pedidos=id).first_or_404()

    data = request.json
    pedido.estado_pedido = EstadoPedido(data['estado_pedido'])

    if data['estado_pedido'] == "ENTREGADO" : 
        deta_ped_filtrado = db.session.query(PedidosProductos).filter(PedidosProductos.id_pedidos == id).all()
        # print (f"id_pedidos: {id}")
        for deta in deta_ped_filtrado:
            producto = db.session.query(Productos).filter(Productos.id == deta.id).first()
            if producto:
                # Evitar stock negativo
                nuevo_stock = max(0, producto.stock - deta.cantidad)
                db.session.query(Productos).filter(Productos.id == deta.id).update({Productos.stock: nuevo_stock})

            # print (f"id_pedidos2: {id}")
            # print (f"cantidad: {deta.cantidad_producto}")
        # print (deta_ped_filtrado.id_pedidos)

    if data['estado_pedido'] == "DEVUELTO" : 
        deta_ped_filtrado = db.session.query(PedidosProductos).filter(PedidosProductos.id_pedidos == id).all()
        # print (f"id_pedidos: {id}")
        for deta in deta_ped_filtrado:
            producto = db.session.query(Productos).filter(Productos.id == deta.id).first()
            if producto:
                db.session.query(Productos).filter(Productos.id == deta.id).update({Productos.stock: producto.stock + deta.cantidad})


    db.session.commit()
    return jsonify(message="Estado del pedido actualizado exitosamente")

@pedidos_user.patch('/api/usuarios/mipedido/<int:id>')
@jwt_required()  # Requiere autenticación JWT
def cancelar_pedido(id):
    # Buscar el pedido por su ID
    pedido = Pedidos.query.filter_by(id_pedidos=id).first_or_404()

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
        productos_data = [{"id": p.id, "cantidad": p.cantidad, "precio": p.precio, "cantidad_producto": p.cantidad_producto, "nombre_producto":p.nombre_producto, "unidad_producto":p.unidad_producto} for p in productos]

        # Acceder al nombre y apellido del usuario relacionado
        nombre_usuario = pedido.usuarios.nombres if pedido.usuarios else None
        apellido_usuario = pedido.usuarios.apellidos if pedido.usuarios else None
        identificacion_usuario = pedido.usuarios.identificacion if pedido.usuarios else None

        pedidos_data.append({
            "id_pedido": pedido.id_pedidos,
            "id_usuario": pedido.id_usuarios,
            "nombre_usuario": nombre_usuario,  # Agregar el nombre del usuario
            "apellido_usuario": apellido_usuario,  # Agregar el apellido del usuario
            "identificacion_usuario": identificacion_usuario,  # Agregar la identificacion del usuario
            "monto_total": pedido.monto_total,
            "direccion": pedido.direccion,
            "forma_entrega": pedido.forma_entrega,
            "barrio": pedido.barrio,
            "ciudad": pedido.ciudad,
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
    productos_data = [{"id": p.id, "cantidad": p.cantidad, "cantidad_producto": p.cantidad_producto, "precio": p.precio, "nombre_producto":p.nombre_producto, "unidad_producto":p.unidad_producto} for p in productos]


    # Acceder al nombre y apellido del usuario relacionado
    nombre_usuario = pedido.usuarios.nombres if pedido.usuarios else None
    apellido_usuario = pedido.usuarios.apellidos if pedido.usuarios else None
    identificacion_usuario = pedido.usuarios.identificacion if pedido.usuarios else None

    # Estructurar la respuesta
    pedido_data = {
        "id_pedido": pedido.id_pedidos,
        "id_usuario": pedido.id_usuarios,
        "nombre_usuario": nombre_usuario,  # Agregar el nombre del usuario
        "apellido_usuario": apellido_usuario,  # Agregar el apellido del usuario
        "identificacion_usuario": identificacion_usuario,  # Agregar la identificacion del usuario
        "monto_total": pedido.monto_total,
        "direccion": pedido.direccion,
        "forma_entrega": pedido.forma_entrega,
        "barrio": pedido.barrio,
        "ciudad": pedido.ciudad,
        "estado_pedido": pedido.estado_pedido.value,
        "fecha_creacion": pedido.fecha_creacion,
        "productos": productos_data
    }

    return jsonify(pedido_data), 200

# TRAER TODOS LOS PEDIDOS
@pedidos_user.get('/api/mod/pedidos')
@jwt_required()  # Puedes mantener o quitar la autenticación según lo necesites
@role_required([Roles.MOD])
def obtener_todos_pedidos_mod():
    # Obtener todos los pedidos de la base de datos
    pedidos = Pedidos.query.all()
    pedidos_data = []

    for pedido in pedidos:
        productos = PedidosProductos.query.filter_by(id_pedidos=pedido.id_pedidos).all()
        productos_data = [{"id": p.id, "cantidad": p.cantidad, "cantidad_producto": p.cantidad_producto, "precio": p.precio, "nombre_producto":p.nombre_producto, "unidad_producto":p.unidad_producto} for p in productos]

        # Acceder al nombre y apellido del usuario relacionado
        nombre_usuario = pedido.usuarios.nombres if pedido.usuarios else None
        apellido_usuario = pedido.usuarios.apellidos if pedido.usuarios else None
        identificacion_usuario = pedido.usuarios.identificacion if pedido.usuarios else None

        pedidos_data.append({
            "id_pedido": pedido.id_pedidos,
            "id_usuario": pedido.id_usuarios,
            "nombre_usuario": nombre_usuario,  # Agregar el nombre del usuario
            "apellido_usuario": apellido_usuario,  # Agregar el apellido del usuario
            "identificacion_usuario": identificacion_usuario,  # Agregar la identificacion del usuario
            "monto_total": pedido.monto_total,
            "direccion": pedido.direccion,
            "forma_entrega": pedido.forma_entrega,
            "barrio": pedido.barrio,
            "ciudad": pedido.ciudad,
            "estado_pedido": pedido.estado_pedido.value,
            "fecha_creacion": pedido.fecha_creacion,
            "productos": productos_data
        })

    return jsonify(pedidos_data), 200

# TRAER LOS PEDIDOS POR ID
@pedidos_user.get('/api/mod/pedidos/<int:pedido_id>')
@jwt_required()  # Puedes mantener o quitar la autenticación según lo necesites
@role_required([Roles.MOD])
def obtener_pedido_por_id_mod(pedido_id):
    # Obtener el pedido por ID sin filtrar por usuario
    pedido = Pedidos.query.get_or_404(pedido_id, description="Pedido no encontrado")
    
    # Obtener los productos asociados al pedido
    productos = PedidosProductos.query.filter_by(id_pedidos=pedido.id_pedidos).all()
    productos_data = [{"id": p.id, "cantidad": p.cantidad, "cantidad_producto": p.cantidad_producto, "precio": p.precio, "nombre_producto":p.nombre_producto, "unidad_producto":p.unidad_producto} for p in productos]

    # Acceder al nombre y apellido del usuario relacionado
    nombre_usuario = pedido.usuarios.nombres if pedido.usuarios else None
    apellido_usuario = pedido.usuarios.apellidos if pedido.usuarios else None
    identificacion_usuario = pedido.usuarios.identificacion if pedido.usuarios else None
    # Estructurar la respuesta
    pedido_data = {
        "id_pedido": pedido.id_pedidos,
        "id_usuario": pedido.id_usuarios,
        "nombre_usuario": nombre_usuario,  # Agregar el nombre del usuario
        "apellido_usuario": apellido_usuario,  # Agregar el apellido del usuario
        "identificacion_usuario": identificacion_usuario,  # Agregar la identificacion del usuario
        "monto_total": pedido.monto_total,
        "direccion": pedido.direccion,
        "forma_entrega": pedido.forma_entrega,
        "barrio": pedido.barrio,
        "ciudad": pedido.ciudad,
        "estado_pedido": pedido.estado_pedido.value,
        "fecha_creacion": pedido.fecha_creacion,
        "productos": productos_data
    }

    return jsonify(pedido_data), 200
