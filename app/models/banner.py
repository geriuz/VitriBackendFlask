from sqlalchemy import Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column
from app.common.config.db import Base 

class Banner(Base):
    __tablename__ = 'banner'

    id_banner: Mapped[int] = mapped_column(Integer, primary_key=True)
    url_imagen: Mapped[str] = mapped_column(String(255))
    posicion_y: Mapped[str] = mapped_column(String(255))

    def to_dict(self):
        return {
            "id_banner": self.id_banner,
            "url_imagen": self.url_imagen,
            "posicion_y": self.posicion_y 
        }

    def __repr__(self):
        return f'<IdBanner {self.id_banner!r},<URLImagen {self.url_imagen!r}, <PosicionY {self.posicion_y!r}>'