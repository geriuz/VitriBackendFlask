from sqlalchemy import Integer, Numeric, DateTime, ForeignKey, String, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.ext.hybrid import hybrid_property
from app.common.config.db import Base 

class PedidosProductos(Base):
    __tablename__ = 'pedidos_productos'

    id_pedidos_productos: Mapped[int] = mapped_column(Integer, primary_key=True)
    cantidad: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    cantidad_producto: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    nombre_producto: Mapped[str] = mapped_column(String(255), nullable=False)
    unidad_producto: Mapped[str] = mapped_column(String(255), nullable=False)

    precio: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    fecha_creacion: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    fecha_actualizacion: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    id_pedidos: Mapped[int] = mapped_column(ForeignKey("pedidos.id_pedidos"))
    id: Mapped[int] = mapped_column(ForeignKey("productos.id"))

    @hybrid_property
    def total_producto(self):
        return self.precio * self.cantidad
    #----------------------------------------------------------------------------------------------#
    # RELACIONES 
    # Reladcion uno a muchos entre pedidos y pagos
    pedidos: Mapped["Pedidos"] = relationship(back_populates="pedidos_productos") #type: ignore
    # Reladcion uno a muchos entre pedidos_productos y productos
    productos: Mapped["Productos"] = relationship(back_populates="pedidos_productos") #type: ignore
    #----------------------------------------------------------------------------------------------#

    def __todict__(self):
        return {
            'cantidad': self.cantidad,
            'precio': self.precio,
            'nombre_producto': self.nombre_producto,
            'unidad_producto': self.unidad_producto,
            'fecha_creacion': self.fecha_creacion,
            'fecha_actualizacion': self.fecha_actualizacion,
            'id_pedidos': self.id_pedidos,
            'cantidad_producto': self.cantidad_producto,
            'id': self.id
        }

    def __repr__(self):
        return f'<id {self.id!r}>, <cantidad {self.cantidad!r}, <precio {self.precio!r}>, <nombre_producto {self.nombre_producto!r}>, <unidad_producto {self.unidad_producto!r}>'