# 🛡️ SOC Sentinel: Honeypot & IPS en Kubernetes

SOC Sentinel es un agente de seguridad activo diseñado para operar dentro de un clúster de Kubernetes. Funciona como un Honeypot y un Sistema de Prevención de Intrusos (IPS) ligero, capaz de detectar tráfico anómalo, registrar eventos en tiempo real y mitigar amenazas automáticamente, enviando alertas directas vía Telegram.

## ⚙️ Arquitectura y Flujo de Trabajo

* **Sensor Activo (Honeypot):** El Pod del Agente expone un servidor web que monitoriza rutas críticas comunes en escaneos de vulnerabilidades (ej. `/admin`, `/script`).
* **Registro Centralizado (PVC):** Los eventos de intrusión se registran en un `PersistentVolumeClaim`, aislando los logs del ciclo de vida del contenedor para auditoría persistente.
* **Mitigación Autónoma (IPS):** El sistema implementa un baneo progresivo. Tras superar el umbral de 3 intentos, se corta la conexión en la capa de aplicación (HTTP 403).
* **Control de Fatiga de Alertas (Alert Fatigue):** Lógica de filtrado que evita el spam a la API de Telegram. Una vez que la IP es bloqueada definitivamente, el tráfico se rechaza de forma silenciosa.


## 🔒 DevSecOps & Hardening (Mejoras de Seguridad)

Este proyecto implementa prácticas de endurecimiento de contenedores para evitar que el propio agente sea un vector de ataque:

* **Usuario sin privilegios:** El contenedor no corre como `root`. Utiliza un usuario de sistema con UID alto.
* **Shell Restringida:** El usuario tiene asignado `/usr/sbin/nologin`, lo que impide ataques de *Reverse Shell* incluso si el código fuera vulnerado.
* **Init Containers:** Uso de contenedores de inicialización para gestionar permisos de lectura/escritura en volúmenes compartidos de forma segura.
* **Gestión de Secretos:** Las API Keys y Tokens no están en el código; se inyectan dinámicamente mediante `K8s Secrets`.

## 🛠️ Stack Tecnológico
* **Lenguaje:** Python 3 (Librerías nativas: `http.server`, `urllib`)
* **Contenedores:** Docker
* **Orquestación:** Kubernetes (Minikube)
* **Seguridad:** NetworkPolicies (Zero Trust), K8s Secrets, RBAC.

## 📂 Estructura del Proyecto
```text
soc-sentinel/
├── k8s/                     # Manifiestos de Kubernetes (Deployment, PVC, Ingress)
│   ├── deployment.yaml      # Configuración del agente con Init Containers
│   └── ...                  # Otros recursos de red y almacenamiento
├── agente.py                # Lógica core: Detección, IPS y Telegram
├── dashboard.py             # Lógica del visor de logs en tiempo real
├── Dockerfile               # Build endurecido del agente (No-root, No-shell)
└── Dockerfile.dashboard     # Build del visor de logs