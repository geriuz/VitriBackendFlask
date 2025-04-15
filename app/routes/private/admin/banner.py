from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app.common.utils.auth import role_required
from app.common.utils.enums.roles import Roles
from app.common.config.db import db
from app.models.banner import Banner

banner_admin = Blueprint('banner_admin', __name__)

@banner_admin.post("/api/admin/banner")
@jwt_required() 
@role_required([Roles.ADMIN])
def guardar_banner():
    data = request.json
    nueva_banner = Banner(url_imagen=data['url_imagen'],
                        posicion_y=data['posicion_y'])
    db.session.add(nueva_banner)
    db.session.commit()

    return jsonify({'message': 'Nuevo banner creada correctamente'}), 201

@banner_admin.get("/api/admin/banner")
@jwt_required() 
@role_required([Roles.ADMIN])
def obtener_banner():
    banners = Banner.query.all()
    return jsonify([banner.to_dict() for banner in banners])

@banner_admin.get("/api/admin/banner/<int:id>")
@jwt_required() 
@role_required([Roles.ADMIN])
def obtener_banner_id(id):
    banner = Banner.query.get_or_404(id, description='Producto no encontrado')
    return jsonify(banner.to_dict())

@banner_admin.patch('/api/admin/banner/<int:id>')
@jwt_required() 
@role_required([Roles.ADMIN])
def actualizar_banner(id):
    banner = Banner.query.get(id)
    if not banner:
        return jsonify({'message': 'Banner no encontrado'}), 404
    data = request.json
    banner.url_imagen = data['url_imagen']
    banner.posicion_y = data['posicion_y']
    db.session.commit()
    return jsonify({'message': 'Banner actualizado satisfactoriamente'}), 200

@banner_admin.delete('/api/admin/banner/<int:id>')
@jwt_required() 
@role_required([Roles.ADMIN])
def eliminar_banner(id):
    banner = Banner.query.get(id)
    if not banner:
        return jsonify({'message': 'Banner no encontrado'}), 404
    db.session.delete(banner)
    db.session.commit()
    return jsonify({'message': 'El banner ha sido eliminada satisactoriamnete'}), 200