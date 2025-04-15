from flask import Blueprint, jsonify, request
from app.common.config.db import db
from app.models.categorias import Categorias

categorias_public = Blueprint('categorias_public', __name__)

@categorias_public.get("/api/publico/categorias")
def obtener_categorias():
    categorias = Categorias.query.all()
    lista_categorias = [{'id_categorias': categoria.id_categorias,
                        'nombre': categoria.nombre, 
                        'url_imagen': categoria.url_imagen} 
                        for categoria in categorias]
    return jsonify(lista_categorias)

@categorias_public.get("/api/publico/categorias/<int:id>")
def obtener_categoria_por_id(id):
    categoria = Categorias.query.get_or_404(id, description='Categoria no encontrada')
    if not categoria:
        return jsonify({'message': 'Categoria no encontrada'}), 404
    return jsonify({'id_categorias': categoria.id_categorias,
                    'nombre': categoria.nombre,
                    'url_imagen': categoria.url_imagen})