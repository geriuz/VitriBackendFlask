from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, set_access_cookies, unset_jwt_cookies
from sqlalchemy.exc import IntegrityError
from app.common.config.db import db
from app.models.usuarios import Usuarios
from app.common.utils.auth import role_required 

autenticacion = Blueprint('autenticacion', __name__)

@autenticacion.post("/api/auth/registro")
def registro_usuario():
    try:
        data = request.json
        nuevo_registro = Usuarios(
            nombres=data['nombres'],
            apellidos=data['apellidos'],
            email=data['email'],
            tipo_identificacion=data['tipo_identificacion'],
            identificacion=data['identificacion'],
            telefono=data['telefono'],
            direccion=data['direccion'],
            barrio=data['barrio'],
            ciudad=data['ciudad']
        )
        nuevo_registro.set_password(data['password'])
        db.session.add(nuevo_registro)
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({'message': f'Error: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error en el servidor: {str(e)}'}), 500

    return jsonify({'message': 'Nuevo usuario creado correctamente'}), 201

@autenticacion.post('/api/auth/login')
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = Usuarios.query.filter_by(email=email).first()

    if user and user.check_password(password):
        # Incluimos el rol en el token
        access_token = create_access_token(identity=user.id_usuarios, additional_claims={'rol': user.rol.value})
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"msg": "Credenciales inválidas"}), 401

@autenticacion.post('/api/auth/logout')
@jwt_required()
def logout():
    # Con tokens Bearer, el logout se maneja del lado del cliente
    return jsonify({"msg": "Logout exitoso"}), 200

@autenticacion.get('/api/auth/perfil')
@jwt_required()
def obtener_perfil():
    current_user_id = get_jwt_identity()
    user = Usuarios.query.get(current_user_id)
    
    if not user:
        return jsonify({"msg": "Usuario no encontrado"}), 404
    
    return jsonify(user.to_dict()), 200