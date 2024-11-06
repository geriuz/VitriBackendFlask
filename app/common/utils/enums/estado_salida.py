from enum import Enum as PyEnum

class EstadoSalida(PyEnum):

    DESCOMPUESTO = "DESCOMPUESTO"
    ROBO = "ROBO"
    VENCIDO = "VENCIDO"
    DONACION = "DONACION"
    ERROR = "ERROR"