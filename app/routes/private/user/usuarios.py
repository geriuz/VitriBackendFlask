from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.common.utils.auth import role_required
from app.common.utils.enums.roles import Roles
from app.common.config.db import db
from app.models.usuarios import Usuarios

usuarios_user = Blueprint('usuarios_user', __name__)

@usuarios_user.get("/api/usuarios/perfil")
@jwt_required() 
def obtener_perfil_usuario():
    current_user_id = get_jwt_identity()
    usuario = Usuarios.query.get(current_user_id)
    if not usuario:
        return jsonify({'message': 'Usuario no encontrado'}), 404
    return jsonify(usuario.to_dict()), 200

@usuarios_user.patch('/api/usuarios/perfil')
@jwt_required()
def actualizar_perfil_usuario():
    current_user_id = get_jwt_identity()
    usuario = Usuarios.query.get(current_user_id)
    if not usuario:
        return jsonify({'message': 'Usuario no encontrado'}), 404
    
    data = request.json
    allowed_fields = ['nombres', 'apellidos', 'email', 'telefono', 'direccion', 'barrio', 'ciudad']  # Campos permitidos
    
    for field in allowed_fields:
        if field in data:
            setattr(usuario, field, data[field])  # Actualizar atributos permitidos
    
    db.session.commit()
    return jsonify({'message': 'Perfil actualizado satisfactoriamente'}), 200
    current_user_id = get_jwt_identity()
    usuario = Usuarios.query.get(current_user_id)
    if not usuario:
        return jsonify({'message': 'Usuario no encontrado'}), 404
    
    data = request.json
    allowed_fields = ['nombres', 'apellidos', 'email', 'telefono', 'direccion', 'barrio', 'ciudad']
    
    for field in allowed_fields:
        if field in data:
            setattr(usuario, field, data[field])
    
    if 'password' in data:
        usuario.set_password(data['password'])
    
    db.session.commit()
    return jsonify({'message': 'Perfil actualizado satisfactoriamente'}), 20