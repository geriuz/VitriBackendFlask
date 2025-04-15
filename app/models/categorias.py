from sqlalchemy import Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.common.config.db import Base 

class Categorias(Base):
    __tablename__ = 'categorias'

    id_categorias: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    url_imagen: Mapped[str] = mapped_column(String(255))
    is_activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    fecha_creacion: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    fecha_actualizacion: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    
    #----------------------------------------------------------------------------------------------#
    # RELACIONES
    # Reladcion uno a muchos entre categorias y productos
    productos: Mapped[list["Productos"]] = relationship( back_populates="categorias", cascade="all, delete-orphan") # type: ignore
    #----------------------------------------------------------------------------------------------#

    def to_dict(self):
        return {
            "id_categorias": self.id_categorias,
            "nombre": self.nombre,
            "url_imagen": self.url_imagen,
            "is_activo": self.is_activo,
            "fecha_creacion": self.fecha_creacion,
            "fecha_actualizacion": self.fecha_actualizacion
        }

    def __repr__(self):
        return f'<Nombre {self.nombre!r}, <Descripcion {self.descripcion!r}, <URLImagen {self.url_imagen!r}, <IsActivo {self.is_activo!r}>'
