from sqlalchemy import Integer, Numeric, DateTime, Enum, ForeignKey, String, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.common.config.db import Base 
from app.common.utils.enums.estado_salida import EstadoSalida

class Salidas(Base):
    __tablename__ = 'salidas'

    id_salidas: Mapped[int] = mapped_column(Integer, primary_key=True)
    fecha_creacion: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    salidas_productos: Mapped[int] = mapped_column(ForeignKey("productos.id"))
    salidas_estado: Mapped[str] = mapped_column(Enum(EstadoSalida, values_callable=lambda obj: [e.value for e in obj]), nullable=False)
    salidas_cantidad: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    observacion: Mapped[str] = mapped_column(String(1000))
    salidas_usuario: Mapped[int] = mapped_column(ForeignKey("usuarios.id_usuarios"))

    #----------------------------------------------------------------------------------------------#
    # RELACIONES 
    # Reladcion uno a muchos entre pedidos y pagos
    usuarios: Mapped["Usuarios"] = relationship(back_populates="salidas") #type: ignore
    # Reladcion uno a muchos entre salidas y productos
    productos: Mapped["Productos"] = relationship(back_populates="salidas") #type: ignore
    #----------------------------------------------------------------------------------------------#

    def to_dict(self):
        return {
            'id_salidas': self.id_salidas,
            'fecha_creacion': self.fecha_creacion,
            'salidas_productos': self.salidas_productos,
            "salidas_estado": self.salidas_estado.value,
            'salidas_cantidad': self.salidas_cantidad,
            'observacion': self.observacion,
            'salidas_usuario': self.salidas_usuario

        }

    def __repr__(self):
        return f'<id_salidas {self.id_salidas!r}>, <fecha_creacion {self.fecha_creacion!r}, <salidas_productos {self.salidas_productos!r}>, <EstadoSalida {self.salidas_estado!r}>, <salidas_cantidad {self.salidas_cantidad!r}>, <observacion {self.observacion!r}>, <salidas_usuario {self.salidas_usuario!r}>'