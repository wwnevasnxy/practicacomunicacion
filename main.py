#!/usr/bin/env python3
"""
==============================================================================
Práctica de Comunicación Multi-Agente — Nevas
==============================================================================
Punto de entrada inicial y verificador de entorno para la arquitectura multi-agente:
- Director / Arquitecto: ChatGPT (Web / Móvil)
- Implementador: Antigravity CLI (agy)
- Auditor / Revisor: Codex CLI (codex)
- Supervisor Humano: Javier (Nevas)
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime

ARCHITECTURE = {
    "director": {
        "name": "ChatGPT",
        "role": "Arquitecto / Director",
        "interface": "Web / App Móvil",
        "description": "Define objetivos, redacta tareas y diseña requerimientos en GitHub Issues."
    },
    "implementer": {
        "name": "Antigravity CLI (agy)",
        "role": "Implementador Técnico Principal",
        "interface": "CLI / Daemon",
        "description": "Desarrolla código, inicializa proyectos y resuelve issues asignados."
    },
    "auditor": {
        "name": "Codex CLI (codex)",
        "role": "Auditor y Revisor de Código",
        "interface": "CLI / Daemon",
        "description": "Audita código, realiza refactorizaciones y revisiones de seguridad."
    },
    "supervisor": {
        "name": "Javier (Nevas)",
        "role": "Supervisor Humano",
        "interface": "Telegram / GitHub Mobile",
        "description": "Monitorea la orquestación y aprueba pasos críticos."
    }
}


def check_tool(command_name: str) -> dict:
    """Verifica si una herramienta CLI está disponible en el PATH del sistema."""
    path = shutil.which(command_name)
    version = None
    if path:
        try:
            res = subprocess.run([command_name, "--version"], capture_output=True, text=True, timeout=5)
            version = (res.stdout or res.stderr).splitlines()[0].strip() if res.returncode == 0 else "Instalado"
        except Exception:
            version = "Instalado (sin versión detectable)"
    return {
        "available": bool(path),
        "path": path or "No encontrado",
        "version": version or "N/A"
    }


def check_git_status() -> dict:
    """Obtiene información sobre el estado del repositorio Git."""
    try:
        branch = subprocess.run(
            ["git", "branch", "--show-current"], capture_output=True, text=True, check=True
        ).stdout.strip()
        remote = subprocess.run(
            ["git", "remote", "get-url", "origin"], capture_output=True, text=True, check=True
        ).stdout.strip()
        last_commit = subprocess.run(
            ["git", "log", "-1", "--format=%h - %s (%ci)"], capture_output=True, text=True, check=True
        ).stdout.strip()
        return {
            "is_git_repo": True,
            "branch": branch,
            "remote": remote,
            "last_commit": last_commit
        }
    except Exception as e:
        return {
            "is_git_repo": False,
            "error": str(e)
        }


def check_environment() -> dict:
    """Realiza un diagnóstico completo de las herramientas y canales de comunicación."""
    telegram_notifier = os.path.expanduser("~/.local/bin/notificar-telegram")
    
    status = {
        "timestamp": datetime.now().isoformat(),
        "architecture": ARCHITECTURE,
        "git": check_git_status(),
        "tools": {
            "git": check_tool("git"),
            "gh": check_tool("gh"),
            "agy": check_tool("agy"),
            "codex": check_tool("codex"),
            "python3": check_tool("python3")
        },
        "channels": {
            "telegram_notifier": {
                "configured": os.path.exists(telegram_notifier) and os.access(telegram_notifier, os.X_OK),
                "path": telegram_notifier
            }
        }
    }
    return status


def print_dashboard(status: dict):
    """Imprime el estado de la arquitectura en consola."""
    print("=" * 70)
    print("🚀 PRÁCTICA DE COMUNICACIÓN MULTI-AGENTE — NEVAS")
    print("=" * 70)
    print(f"🕒 Timestamp: {status['timestamp']}")
    
    git_info = status["git"]
    if git_info.get("is_git_repo"):
        print(f"📦 Repositorio: {git_info.get('remote')}")
        print(f"🌿 Rama actual: {git_info.get('branch')}")
        print(f"🔖 Último commit: {git_info.get('last_commit')}")
    else:
        print("⚠️ No se detectó un repositorio git válido.")

    print("\n" + "-" * 70)
    print("👥 ROLES DE LA ARQUITECTURA")
    print("-" * 70)
    for key, role in status["architecture"].items():
        print(f"• {role['role']} ({role['name']}) [{role['interface']}]:")
        print(f"  {role['description']}")

    print("\n" + "-" * 70)
    print("🛠️ HERRAMIENTAS Y AGENTES")
    print("-" * 70)
    for tool, info in status["tools"].items():
        icon = "✅" if info["available"] else "❌"
        print(f"{icon} {tool.ljust(8)}: {info['version']} ({info['path']})")

    tg = status["channels"]["telegram_notifier"]
    tg_icon = "✅" if tg["configured"] else "❌"
    print(f"{tg_icon} telegram: {'Configurado' if tg['configured'] else 'No disponible'} ({tg['path']})")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description="Punto de inicio y diagnóstico para la comunicación multi-agente."
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emitir diagnóstico en formato JSON estructurado."
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Ejecutar comprobación de estado y mostrar dashboard."
    )
    args = parser.parse_args()

    status = check_environment()

    if args.json:
        print(json.dumps(status, indent=2, ensure_ascii=False))
    else:
        print_dashboard(status)


if __name__ == "__main__":
    main()
