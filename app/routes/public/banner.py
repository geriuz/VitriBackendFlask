from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app.common.utils.auth import role_required
from app.common.utils.enums.roles import Roles
from app.common.config.db import db
from app.models.banner import Banner

banner_public = Blueprint('banner_public', __name__)

@banner_public.get("/api/publico/banner")
def obtener_banner():
    banners = Banner.query.all()
    return jsonify([banner.to_dict() for banner in banners])