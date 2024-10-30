from sqlalchemy import Integer, Numeric, Enum,  DateTime, ForeignKey, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from common.config.db import Base 
from common.utils.enums.estado_pedido import EstadoPedido

class Pedidos(Base):
    __tablename__ = 'pedidos'

    id_pedidos: Mapped[int] = mapped_column(Integer, primary_key=True)
    monto_total: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    estado_pedido: Mapped[EstadoPedido] = mapped_column(Enum(EstadoPedido), nullable=False)

    fecha_creacion: Mapped[DateTime] = mapped_column(DateTime, default=func.now())

    id_usuarios: Mapped[int] = mapped_column(ForeignKey("usuarios.id_usuarios"))
    # id_pagos: Mapped[int] = mapped_column(ForeignKey("pagos.id_pagos"))

    def obtener_total_precio_pedido(self) -> float:
        return sum(producto.get_total_producto() for producto in self.pedido_productos)
    #----------------------------------------------------------------------------------------------#
    # RELACIONES 
    # Reladcion uno a muchos entre usuarios y pedidos
    usuarios: Mapped["Usuarios"] = relationship(back_populates="pedidos") # type: ignore
    # Reladcion uno a muchos entre pedidos y productos
    pedidos_productos: Mapped[list["PedidosProductos"]] = relationship(back_populates="pedidos") # type: ignore
    # Reladcion uno a muchos entre pagos y pedidos
    # pagos: Mapped["Pagos"] = relationship(back_populates="pedidos") # type: ignore
    #----------------------------------------------------------------------------------------------#

    def __todict__(self):
        return {
            "email": self.email,
            "monto_total": self.monto_total,
            "estado_pedido": self.estado_pedido.name,
            "id_pagos": self.id_pagos,
            "id_usuarios": self.id_usuarios
        }    

    def __repr__(self):
        return f'<id {self.id!r}>, <email {self.email!r}, <monto_total {self.monto_total!r}, <estado_pedido {self.estado_pedido!r}>'