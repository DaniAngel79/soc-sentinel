FROM python:3.9-slim

ENV PYTHONUNBUFFERED=1

# 1. Crear el usuario de sistema seguro (sin la bandera obsoleta)
RUN useradd --system --shell /usr/sbin/nologin socuser

WORKDIR /app

# 2. Copiar el código y asignarle la propiedad
COPY --chown=socuser:socuser agente.py .

# 3. Crear el directorio de logs y darle permisos al usuario
RUN mkdir -p /app/logs && chown -R socuser:socuser /app/logs

EXPOSE 8080

# 4. Cambiar el contexto de ejecución
USER socuser

CMD ["python", "agente.py"]