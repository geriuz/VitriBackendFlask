from sqlalchemy import Integer, Numeric, DateTime, Enum, String, func
from common.utils.enums.metodo_pago import MetodoPago
from sqlalchemy.orm import relationship, Mapped, mapped_column
from common.config.db import Base 

class Pagos(Base):
    __tablename__ = 'pagos'

    id_pagos: Mapped[int] = mapped_column(Integer, primary_key=True)
    metodo_pago: Mapped[str] = mapped_column(Enum(MetodoPago), nullable=False)
    monto: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    numero_transaccion: Mapped[str] = mapped_column(String(255))
    fecha_pago: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    #----------------------------------------------------------------------------------------------#
    # RELACIONES 
    # Reladcion uno a muchos entre pedidos y pedidos_productos
    pedidos: Mapped[list["Pedidos"]] = relationship(back_populates="pagos") #type: ignore
    #----------------------------------------------------------------------------------------------#


    def __todict__(self):
        return {
            'metodo_pago': self.metodo_pago,
            'monto': self.monto,
            'numero_transaccion': self.numero_transaccion,
            'fecha_pago': self.fecha_pago
        }

    def __repr__(self):
        return f'<id {self.id!r}>, <metodo_pago {self.metodo_pago!r}, <monto {self.monto!r}, <numero_transaccion {self.numero_transaccion!r}, <fecha_pago {self.fecha_pago!r}>'