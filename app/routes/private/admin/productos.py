from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.common.utils.auth import role_required
from app.common.utils.enums.roles import Roles
from app.common.config.db import db
from app.models.productos import Productos
from sqlalchemy.exc import IntegrityError

productos_admin = Blueprint('productos_admin', __name__)

@productos_admin.post("/api/admin/productos")
@jwt_required() 
@role_required([Roles.ADMIN])
def guardar_productos():
    data = request.json
    try:
        nuevo_producto = Productos(
            sku=data['sku'],
            nombre=data['nombre'],
            descripcion=data['descripcion'],
            url_imagen=data['url_imagen'],
            url_ficha_tecnica=data['url_ficha_tecnica'],
            unidad_producto=data['unidad_producto'],
            cantidad=data['cantidad'],
            max_usuario=data['max_usuario'],
            precio=data['precio'],
            is_promocion=data.get('is_promocion', False),
            anunciar=data.get('anunciar', False),
            stock=data['stock'],
            descuento=data.get('descuento', 0),
            id_categorias=data['id_categorias'],
            id_usuarios=get_jwt_identity(),
        )
        db.session.add(nuevo_producto)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'message': 'Error: El SKU ya existe'}), 400
    except KeyError as e:
        return jsonify({'message': f'Error: Falta el campo {str(e)}'}), 400
    except ValueError as e:
        return jsonify({'message': f'Error: {str(e)}'}), 400

    return jsonify({'message': 'Nuevo producto creado correctamente'}), 201

@productos_admin.get("/api/admin/productos")
@jwt_required() 
def obtener_productos():
    productos = Productos.query.all()
    return jsonify([producto.to_dict() for producto in productos])

@productos_admin.get("/api/admin/productos/<int:id>")
@jwt_required() 
@role_required([Roles.ADMIN])
def obtener_producto_por_id(id):
    producto = Productos.query.get_or_404(id, description='Producto no encontrado')
    return jsonify(producto.to_dict())

@productos_admin.patch('/api/admin/productos/<int:id>')
@jwt_required() 
@role_required([Roles.ADMIN])
def actualizar_producto(id):
    producto = Productos.query.get_or_404(id, description='Producto no encontrado')
    data = request.json
    campos_permitidos = [
        'nombre', 'descripcion', 'url_imagen', 'url_ficha_tecnica', 'unidad_producto',
        'cantidad', 'max_usuario', 'precio', 'is_promocion', 'stock', 'descuento', 'is_activo','anunciar',
        'id_categorias', 'fecha_inicio_descuento', 'fecha_fin_descuento'
    ]
    
    try:
        for campo in campos_permitidos:
            if campo in data:
                setattr(producto, campo, data[campo])
        
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'message': 'Error: El SKU ya existe'}), 400
    except ValueError as e:
        return jsonify({'message': f'Error: {str(e)}'}), 400

    return jsonify({'message': 'Producto actualizado satisfactoriamente'}), 200

@productos_admin.delete('/api/admin/productos/<int:id>')
@jwt_required() 
@role_required([Roles.ADMIN])
def eliminar_producto(id):
    producto = Productos.query.get_or_404(id, description='Producto no encontrado')
    db.session.delete(producto)
    db.session.commit()
    return jsonify({'message': 'El producto ha sido eliminado satisfactoriamente'}), 200