from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app.common.utils.auth import role_required
from app.common.utils.enums.roles import Roles
from app.common.config.db import db
from app.models.salidas import Salidas
from app.models.productos import Productos

salidas_admin = Blueprint('salidas_admin', __name__)

@salidas_admin.post("/api/admin/salidas")
@jwt_required() 
@role_required([Roles.ADMIN])
def guardar_salidas():
    data = request.json
    
    # Crear la nueva salida
    nueva_salida = Salidas(
        salidas_productos=data['salidas_productos'],
        salidas_estado=data['salidas_estado'],
        salidas_cantidad=data['salidas_cantidad'],
        observacion=data['observacion'],
        salidas_usuario=data['salidas_usuario']
    )
    db.session.add(nueva_salida)
    
    # Actualizar el stock del producto relacionado
    producto = Productos.query.get(data['salidas_productos'])
    if not producto:
        return jsonify({'message': 'Producto no encontrado'}), 404

    # resta la cantidad de la salida al stock del producto
    producto.stock -= data['salidas_cantidad']
    
    # Guardar todos los cambios en la base de datos
    db.session.commit()

    return jsonify({'message': 'Nueva Salida creada y stock actualizado correctamente'}), 201


@salidas_admin.get("/api/admin/salidas")
@jwt_required() 
@role_required([Roles.ADMIN])
def obtener_salidas():
    salidas = Salidas.query.all()
    return jsonify([salida.to_dict() for salida in salidas])

@salidas_admin.get("/api/admin/salidas/<int:id>")
@jwt_required() 
@role_required([Roles.ADMIN])
def salidas_por_id(id):
    salida = Salidas.query.get_or_404(id, description='Producto no encontrado')
    return jsonify(salida.to_dict())

