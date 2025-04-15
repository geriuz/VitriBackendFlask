from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app.common.utils.auth import role_required
from app.common.utils.enums.roles import Roles
from app.common.config.db import db
from app.models.entradas import Entradas
from app.models.productos import Productos

entradas_admin = Blueprint('entradas_admin', __name__)

@entradas_admin.post("/api/admin/entradas")
@jwt_required() 
@role_required([Roles.ADMIN])
def guardar_entradas():
    data = request.json
    
    # Crear la nueva entrada
    nueva_entrada = Entradas(
        entrada_productos=data['entrada_productos'],
        entrada_cantidad=data['entrada_cantidad'],
        observacion=data['observacion'],
        entrada_usuario=data['entrada_usuario']
    )
    db.session.add(nueva_entrada)
    
    # Actualizar el stock del producto relacionado
    producto = Productos.query.get(data['entrada_productos'])
    if not producto:
        return jsonify({'message': 'Producto no encontrado'}), 404

    # Sumar la cantidad de la entrada al stock del producto
    producto.stock += data['entrada_cantidad']
    
    # Guardar todos los cambios en la base de datos
    db.session.commit()

    return jsonify({'message': 'Nueva Entrada creada y stock actualizado correctamente'}), 201


@entradas_admin.get("/api/admin/entradas")
@jwt_required() 
@role_required([Roles.ADMIN])
def obtener_entradas():
    entradas = Entradas.query.all()
    return jsonify([entrada.to_dict() for entrada in entradas])

@entradas_admin.get("/api/admin/entradas/<int:id>")
@jwt_required() 
@role_required([Roles.ADMIN])
def obtener_entrada_por_id(id):
    entrada = Entradas.query.get_or_404(id, description='Producto no encontrado')
    return jsonify(entrada.to_dict())

@entradas_admin.patch('/api/admin/entradas/<int:id>')
@jwt_required() 
@role_required([Roles.ADMIN])
def actualizar_entrada(id):
    entrada = Entradas.query.get(id)
    if not entrada:
        return jsonify({'message': 'Entrada no encontrada'}), 404
    data = request.json
    entrada.entrada_productos = data['entrada_productos']
    entrada.entrada_cantidad = data['entrada_cantidad']
    entrada.observacion = data['observacion']
    entrada.entrada_usuario = data['entrada_usuario']
    db.session.commit()
    return jsonify({'message': 'Entrada actualizada satisfactoriamente'}), 200

@entradas_admin.delete('/api/admin/entradas/<int:id>')
@jwt_required() 
@role_required([Roles.ADMIN])
def eliminar_entrada(id):
    entrada = Entradas.query.get(id)
    if not entrada:
        return jsonify({'message': 'Entrada no encontrada'}), 404
    db.session.delete(entrada)
    db.session.commit()
    return jsonify({'message': 'La entrada ha sido eliminada satisactoriamnete'}), 200