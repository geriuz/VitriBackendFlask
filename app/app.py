from flask import Flask
from flask_jwt_extended import JWTManager
from datetime import timedelta
from common.config.db import db
from flask_cors import CORS

from models import * # Importación de los modelos
from routes.public import categorias_public, productos_public, banner_public # Importación blueprints de rutas publicas
from routes.private.admin import productos_admin, usuarios_admin, categorias_admin, entradas_admin, salidas_admin, banner_admin # Importación blueprints de rutas privadas rol admin
from routes.private.user import pedidos_user, usuarios_user # Importación blueprints de rutas privadas rol usuario
from routes.authentication.autenticacion import autenticacion  # Importación de los Blueprints de autenticación

# -------------------------------------------------------------------------------------------------------- #
# Creación de la aplicación Flask
# -------------------------------------------------------------------------------------------------------- #
app = Flask(__name__)
CORS(app)
4
# -------------------------------------------------------------------------------------------------------- #
# Configuración de la conexión de SQLAlchemy a la Base de Datos
# -------------------------------------------------------------------------------------------------------- #
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:1066@localhost/vitridb?charset=utf8mb4"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True  # Habilitar el echo para ver las sentencias SQL

# -------------------------------------------------------------------------------------------------------- #
# JSon Web Token (JWT) configuracion
# -------------------------------------------------------------------------------------------------------- #
app.config['JWT_SECRET_KEY'] = 'iDJa44PZXLrQ6X396ZKYE8WGXG4Gt2LFE3fyV0TinuTtBnzabGhp6167VFwJPuz2qbv3M8ueG78PTTryHKyacfUc28T9Pm92aztY'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=2)

jwt = JWTManager(app)

# -------------------------------------------------------------------------------------------------------- #
# Inicialización de SQLAlchemy con la aplicación
# -------------------------------------------------------------------------------------------------------- #
db.init_app(app)

# -------------------------------------------------------------------------------------------------------- #
# Creación de las tablas en la base de datos a través de los modelos con SQLAlchemy
# -------------------------------------------------------------------------------------------------------- #
with app.app_context():
    db.create_all()

# -------------------------------------------------------------------------------------------------------- #
# Registo de Blueprints
# -------------------------------------------------------------------------------------------------------- #
# Registro de Blueprints rutas publicas
app.register_blueprint(productos_public)
app.register_blueprint(categorias_public)
app.register_blueprint(banner_public)
# Registro de Blueprints rutas privadas rol administrativo
app.register_blueprint(usuarios_admin)
app.register_blueprint(productos_admin)
app.register_blueprint(categorias_admin)
app.register_blueprint(entradas_admin)
app.register_blueprint(salidas_admin)
app.register_blueprint(banner_admin)
# Registro de Blueprints rutas privadas rol usuario
app.register_blueprint(pedidos_user)
app.register_blueprint(usuarios_user)
# Registro de Blueprints rutas de autenticación
app.register_blueprint(autenticacion)
# -------------------------------------------------------------------------------------------------------- #
# Inicializador de la aplicación
# -------------------------------------------------------------------------------------------------------- #
if __name__ == '__main__':
    app.run(debug=True)



