# 1. Usar una imagen ligera de Python
FROM python:3.11-slim

# 2. Definir dónde vivirá el código en el servidor
WORKDIR /app

# 3. Copiar la lista de librerías e instalarlas
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copiar todo tu código al servidor
COPY . .

# 5. Comando para encender el servidor en el puerto 8080 (el que usa Google Cloud)
CMD ["python", "app.py"]