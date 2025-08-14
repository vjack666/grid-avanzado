# CONFIGURACIÓN SEGURA DE TERMINALES - TRADING GRID
# ================================================
# 
# Esta configuración asegura que el sistema Trading Grid opere
# de manera segura sin interferir con otros bots o terminales.
#
# REGLAS DE SEGURIDAD:
# - Solo gestiona procesos específicos del Trading Grid
# - NO cierra terminales externos o de otros bots
# - Usa identificadores únicos para aislamiento
# - Respeta variables de entorno del workspace

SAFE_TERMINAL_CONFIG = {
    "mode": "safe_isolated",
    "workspace_isolation": True,
    "respect_external_terminals": True,
    "fundednext_management": {
        "auto_start": True,
        "exclusive_use": True,
        "close_other_mt5": False,  # CRÍTICO: No cerrar otros MT5
        "safe_detection": True
    },
    "terminal_identification": {
        "grid_markers": [
            "TRADING_GRID_WORKSPACE",
            "GRID_SYSTEM_MODE", 
            "FUNDEDNEXT_TERMINAL_PATH"
        ],
        "require_markers": True,
        "respect_unmarked_terminals": True
    },
    "security": {
        "log_terminal_operations": True,
        "verify_before_action": True,
        "safe_mode_enabled": True,
        "protection_level": "maximum"
    }
}

# Configuración del entorno de workspace
WORKSPACE_ENV_CONFIG = {
    "TRADING_GRID_WORKSPACE": "${workspaceFolder}",
    "FUNDEDNEXT_TERMINAL_PATH": "C:\\Program Files\\FundedNext MT5 Terminal\\terminal64.exe",
    "GRID_SYSTEM_MODE": "WORKSPACE_ISOLATED",
    "SAFE_TERMINAL_MODE": "ENABLED",
    "BOT_PROTECTION": "ACTIVE"
}

# Configuración de logs de seguridad
SECURITY_LOG_CONFIG = {
    "log_terminal_discovery": True,
    "log_process_actions": True,
    "log_safety_checks": True,
    "alert_external_terminals": True,
    "preserve_external_processes": True
}

print("✅ Configuración segura de terminales cargada")
print("🛡️ Modo de protección de bots activado")
print("🎯 Solo FundedNext MT5 será gestionado por el sistema")
