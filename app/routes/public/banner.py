from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from common.utils.auth import role_required
from common.utils.enums.roles import Roles
from common.config.db import db
from models.banner import Banner

banner_public = Blueprint('banner_public', __name__)

@banner_public.get("/api/publico/banner")
def obtener_banner():
    banners = Banner.query.all()
    return jsonify([banner.to_dict() for banner in banners])