# Usa una imagen de Python
FROM python:3.10

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos de la app al contenedor
COPY . /app

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto en el que correrá Flask
EXPOSE 8080

# Comando para ejecutar la app
CMD ["python", "app/app.py"]
