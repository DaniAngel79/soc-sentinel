FROM python:3.9-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY agente.py .
EXPOSE 8080
CMD ["python", "agente.py"]
