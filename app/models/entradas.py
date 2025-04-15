from sqlalchemy import Integer, Numeric, DateTime, ForeignKey, String, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.common.config.db import Base 

class Entradas(Base):
    __tablename__ = 'entradas'

    id_entrada: Mapped[int] = mapped_column(Integer, primary_key=True)
    fecha_creacion: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    entrada_productos: Mapped[int] = mapped_column(ForeignKey("productos.id"))
    entrada_cantidad: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    observacion: Mapped[str] = mapped_column(String(1000))
    entrada_usuario: Mapped[int] = mapped_column(ForeignKey("usuarios.id_usuarios"))

    #----------------------------------------------------------------------------------------------#
    # RELACIONES 
    # Reladcion uno a muchos entre pedidos y pagos
    usuarios: Mapped["Usuarios"] = relationship(back_populates="entradas") #type: ignore
    # Reladcion uno a muchos entre entradas y productos
    productos: Mapped["Productos"] = relationship(back_populates="entradas") #type: ignore
    #----------------------------------------------------------------------------------------------#

    def to_dict(self):
        return {
            'id_entrada': self.id_entrada,
            'fecha_creacion': self.fecha_creacion,
            'entrada_productos': self.entrada_productos,
            'entrada_cantidad': self.entrada_cantidad,
            'observacion': self.observacion,
            'entrada_usuario': self.entrada_usuario

        }

    def __repr__(self):
        return f'<id_entrada {self.id_entrada!r}>, <fecha_creacion {self.fecha_creacion!r}, <entrada_productos {self.entrada_productos!r}>, <entrada_cantidad {self.entrada_cantidad!r}>, <observacion {self.observacion!r}>, <entrada_usuario {self.entrada_usuario!r}>'