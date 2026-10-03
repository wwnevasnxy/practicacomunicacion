# 🚀 Práctica de Comunicación Multi-Agente — Nevas

Este repositorio es una prueba de concepto para la arquitectura de agentes autónomos:
- **Director / Arquitecto:** ChatGPT (Web / Móvil)
- **Implementador:** Antigravity CLI (`agy`)
- **Auditor / Revisor:** Codex CLI (`codex`)
- **Supervisor:** Javier (Nevas)

## Estado actual
- Conexión Git y GitHub CLI (`gh`): **Activa y operativa**
- Monitoreo y ciclo de notificaciones: **En prueba de validación móvil**
- Archivo principal del proyecto: [`main.py`](main.py) **implementado y funcional**

## Estructura del Proyecto
```text
.
├── .gitignore         # Exclusiones de Git para entorno Python
├── README.md          # Documentación del proyecto y roles
└── main.py            # Punto de entrada inicial y diagnóstico de entorno
```

## Uso de `main.py`
Para ejecutar el diagnóstico de entorno y verificar el estado de los agentes y canales:

```bash
# Mostrar panel de estado en consola:
python3 main.py

# Emitir diagnóstico estructurado en formato JSON:
python3 main.py --json
```
