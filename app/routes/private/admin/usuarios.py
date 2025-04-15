from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app.common.utils.auth import role_required
from app.common.utils.enums.roles import Roles
from sqlalchemy.exc import IntegrityError
from app.common.config.db import db
from app.models.usuarios import Usuarios

usuarios_admin = Blueprint('usuarios_admin', __name__)

@usuarios_admin.post("/api/admin/usuarios/registro")
@jwt_required() 
@role_required([Roles.ADMIN])
def guardar_usuarios():
    data = request.json
    try:
        nuevo_registro = Usuarios(
            nombres=data['nombres'], 
            apellidos=data['apellidos'], 
            email=data['email'],
            rol=Roles(data['rol']),
            tipo_identificacion=data['tipo_identificacion'],
            identificacion=data['identificacion'],
            telefono=data['telefono'],
            direccion=data['direccion'],
            barrio=data['barrio'],
            ciudad=data['ciudad'],
            is_activo=data.get('is_activo', True)
        )
        nuevo_registro.set_password(data['password'])
        db.session.add(nuevo_registro)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'message': 'Error: El email o la identificación ya están en uso'}), 400
    except KeyError as e:
        return jsonify({'message': f'Error: Falta el campo {str(e)}'}), 400
    except ValueError as e:
        return jsonify({'message': f'Error: {str(e)}'}), 400

    return jsonify({'message': 'Nuevo usuario creado correctamente'}), 201

@usuarios_admin.get("/api/admin/usuarios")
@jwt_required() 
@role_required([Roles.ADMIN])
def obtener_usuarios():
    usuarios = Usuarios.query.all()
    lista_usuarios = [usuario.to_dict() for usuario in usuarios]
    return jsonify(lista_usuarios)

@usuarios_admin.get("/api/admin/usuarios/<int:id>")
@jwt_required() 
@role_required([Roles.ADMIN])
def obtener_usuario_por_id(id):
    usuario = Usuarios.query.get_or_404(id, description='Usuario no encontrado')
    return jsonify(usuario.to_dict())

@usuarios_admin.patch('/api/admin/usuarios/<int:id>')
@jwt_required() 
@role_required([Roles.ADMIN])
def actualizar_usuario(id):
    usuario = Usuarios.query.get_or_404(id, description='Usuario no encontrado')
    data = request.json
    campos_permitidos = ['nombres', 'apellidos', 'email', 'rol', 'tipo_identificacion', 'identificacion', 'telefono', 'direccion', 'barrio', 'ciudad', 'is_activo']
    
    try:
        for campo in campos_permitidos:
            if campo in data:
                if campo == 'rol':
                    setattr(usuario, campo, Roles(data[campo]))
                else:
                    setattr(usuario, campo, data[campo])
        
        if 'password' in data:
            usuario.set_password(data['password'])
        
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'message': 'Error: El email o la identificación ya están en uso'}), 400
    except ValueError as e:
        return jsonify({'message': f'Error: {str(e)}'}), 400

    return jsonify({'message': 'Usuario actualizado satisfactoriamente'}), 200

@usuarios_admin.delete('/api/admin/usuarios/<int:id>')
@jwt_required() 
@role_required([Roles.ADMIN])
def eliminar_usuario(id):
    usuario = Usuarios.query.get_or_404(id, description='Usuario no encontrado')
    db.session.delete(usuario)
    db.session.commit()
    return jsonify({'message': 'El usuario ha sido eliminado satisfactoriamente'}), 200