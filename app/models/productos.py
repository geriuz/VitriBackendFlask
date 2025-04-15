from sqlalchemy import (Integer, Numeric, String, Boolean, Enum, Float, DateTime, ForeignKey, Date, func)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.common.config.db import Base
from app.common.utils.enums.unidad_producto import UnidadProducto


class Productos(Base):
    __tablename__ = "productos"

    id: Mapped[int] = mapped_column(primary_key=True)
    sku: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    descripcion: Mapped[str] = mapped_column(String(1000))
    url_imagen: Mapped[str] = mapped_column(String(255))
    url_ficha_tecnica: Mapped[str] = mapped_column(String(255))
    unidad_producto: Mapped[str] = mapped_column(Enum(UnidadProducto, values_callable=lambda obj: [e.value for e in obj]), nullable=False)
    cantidad: Mapped[int] = mapped_column(Integer)
    max_usuario: Mapped[int] = mapped_column(Integer)
    precio: Mapped[float] = mapped_column(Float, nullable=False)
    is_promocion: Mapped[bool] = mapped_column(Boolean, nullable=False)
    stock: Mapped[int] = mapped_column(Integer, nullable=False)
    is_activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    anunciar: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    descuento: Mapped[float] = mapped_column(Numeric(10, 2))
    fecha_inicio_descuento: Mapped[Date] = mapped_column(Date, default=func.now())
    fecha_fin_descuento: Mapped[Date] = mapped_column(Date, default=func.now())
    fecha_creacion: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    fecha_actualizacion: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    id_categorias: Mapped[int] = mapped_column(ForeignKey("categorias.id_categorias"))
    id_usuarios: Mapped[int] = mapped_column(ForeignKey("usuarios.id_usuarios"))
    # ----------------------------------------------------------------------------------------------#
    # RELACIONES
    # Relacion uno a muchos entre categorias y productos
    categorias: Mapped["Categorias"] = relationship(back_populates="productos")  # type: ignore
    # Relacion uno a muchos entre usuarios y productos
    usuarios: Mapped["Usuarios"] = relationship(back_populates="productos")  # type: ignore
    # Relacion uno a muchos entre pedidos_productos y productos
    pedidos_productos: Mapped[list["PedidosProductos"]] = relationship(back_populates="productos")  # type: ignore
    # Relacion uno a muchos entre entradas y productos
    entradas: Mapped[list["Entradas"]] = relationship(back_populates="productos")   # type: ignore
    # Relacion uno a muchos entre salidas y productos
    salidas: Mapped[list["Salidas"]] = relationship(back_populates="productos")   # type: ignore

    # ----------------------------------------------------------------------------------------------#

    def set_initial_values(self):
        self.is_activo = True

    def to_dict(self):
        return {
            "id": self.id,
            "sku": self.sku,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "url_imagen": self.url_imagen,
            "url_ficha_tecnica": self.url_ficha_tecnica,
            "unidad_producto": self.unidad_producto.value,
            "cantidad": self.cantidad,
            "max_usuario": self.max_usuario,
            "precio": self.precio,
            "is_promocion": self.is_promocion,
            "stock": self.stock,
            "is_activo": self.is_activo,
            "anunciar": self.anunciar,
            "descuento": self.descuento,
            "id_categorias": self.id_categorias,
            "id_usuarios": self.id_usuarios,
            "fecha_inicio_descuento": self.fecha_inicio_descuento,
            "fecha_fin_descuento": self.fecha_fin_descuento,
            "fecha_creacion": self.fecha_creacion,
            "fecha_actualizacion": self.fecha_actualizacion
        }

    def __repr__(self):
        return f"<SKU {self.sku!r}>, <Nombre {self.nombre!r}, <URLImagen {self.url_imagen!r}, <URLFichaTecnica {self.url_ficha_tecnica!r}, <UnidadProducto {self.unidad_producto!r}, <Cantidad {self.cantidad!r}, <MaxUsuario {self.max_usuario!r}, <Precio {self.precio!r},<IsPromocion {self.is_promocion!r},<IsStock {self.stock!r},<IsActivo {self.is_activo!r},<Anunciar {self.anunciar!r}, <Descuento {self.descuento!r}, <FechaInicioDescuento {self.fecha_inicio_descuento!r}, <FechaFinDescuento {self.fecha_fin_descuento!r}>"
