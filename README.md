# 🛡️ SOC Sentinel: Honeypot & IPS en Kubernetes

SOC Sentinel es un agente de seguridad activo diseñado para operar dentro de un clúster de Kubernetes. Funciona como un Honeypot y un Sistema de Prevención de Intrusos (IPS) ligero, capaz de detectar tráfico anómalo, registrar eventos en tiempo real y mitigar amenazas automáticamente, enviando alertas directas vía Telegram.

## ⚙️ Arquitectura y Flujo de Trabajo

1. **Sensor Activo (Honeypot):** El Pod del Agente expone un servidor web que monitoriza rutas críticas comunes en escaneos de vulnerabilidades (ej. `/admin`, `/script`).
2. **Registro Centralizado (PVC):** Los eventos de intrusión se registran en un `PersistentVolumeClaim` con acceso `ReadWriteMany`, aislando los logs del ciclo de vida del contenedor.
3. **Notificación en Tiempo Real:** Ante un intento de acceso, el agente extrae credenciales de un K8s Secret y consume la API de Telegram para notificar al equipo SOC instantáneamente.
4. **Mitigación Autónoma (IPS):** El agente mantiene un control de estado. Si una IP de origen supera el umbral de 3 intentos maliciosos, el sistema corta la conexión en la capa de aplicación (HTTP 403) aislando al atacante.

## 🛠️ Stack Tecnológico
* **Lenguaje:** Python 3 (Librerías nativas: `http.server`, `urllib`)
* **Contenedores:** Docker
* **Orquestación:** Kubernetes (Minikube)
* **Networking & Seguridad:** NetworkPolicies, Ingress, K8s Secrets
* **Integración:** Telegram Bot API

## 📂 Estructura del Proyecto
```text
soc-sentinel/
├── k8s/                     # Manifiestos de Kubernetes
│   ├── deployment.yaml      # Despliegue del Agente (IPS)
│   ├── dashboard-deploy.yaml# Despliegue del Dashboard de visualización
│   ├── network-policy.yaml  # Reglas de firewall interno (Zero Trust)
│   ├── service.yaml         # Exposición de puertos
│   ├── ingress.yaml         # Reglas de enrutamiento y SSL
│   ├── soc-pvc.yaml         # Reclamación de volumen persistente
│   └── storage.yaml         # Volumen persistente (HostPath)
├── agente.py                # Lógica core del IPS y Honeypot
├── dashboard.py             # Lógica del visor de logs
├── Dockerfile               # Build de la imagen del agente
└── Dockerfile.dashboard     # Build de la imagen del dashboard
