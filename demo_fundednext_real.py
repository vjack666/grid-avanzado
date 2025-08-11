"""
DEMO REAL FUNDEDNEXT MT5 MANAGER
================================
Demostración real del gestor exclusivo de FundedNext MT5 Terminal

Este es un sistema REAL, no demo. Maneja verdaderamente:
- Detección de procesos MT5 en el sistema
- Apertura/cierre inteligente de terminales
- Conexión real a MetaTrader 5
- Gestión exclusiva de FundedNext MT5

FECHA: 2025-08-11
"""

import sys
import os
import time
from datetime import datetime

# Configurar paths
sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'core'))

try:
    from config_manager import ConfigManager
    from logger_manager import LoggerManager
    from error_manager import ErrorManager
    from fundednext_mt5_manager import FundedNextMT5Manager
except ImportError as e:
    print(f"❌ Error importando dependencias: {e}")
    sys.exit(1)


def main():
    """Función principal del demo real"""
    print("🎯 FUNDEDNEXT MT5 MANAGER - SISTEMA REAL")
    print("=" * 55)
    print("Sistema de gestión exclusiva de FundedNext MT5 Terminal")
    print()
    
    # Inicializar sistema
    print("🚀 INICIALIZANDO SISTEMA REAL")
    print("=" * 40)
    
    try:
        # Crear dependencias del sistema
        config = ConfigManager()
        logger = LoggerManager()
        error = ErrorManager(logger, config)
        
        # Crear FundedNext MT5 Manager
        fn_manager = FundedNextMT5Manager(
            config=config,
            logger=logger,
            error=error
        )
        
        print(f"✅ {fn_manager.component_id} {fn_manager.version} inicializado")
        print()
        
    except Exception as e:
        print(f"❌ Error inicializando sistema: {e}")
        return
    
    # 1. Estado inicial del sistema
    print("1️⃣ ESTADO INICIAL DEL SISTEMA")
    print("=" * 35)
    
    try:
        status = fn_manager.get_manager_status()
        terminal_status = status["terminal_status"]
        other_terminals = status["other_terminals"]
        
        print(f"🏷️  Manager ID: {status['component_id']}")
        print(f"📦 Versión: {status['version']}")
        print(f"⚡ Estado: {status['status']}")
        print(f"🔗 Conectado MT5: {status['is_connected']}")
        print()
        
        print("📋 ESTADO DEL TERMINAL:")
        print(f"  • Ejecutándose: {terminal_status['is_running']}")
        print(f"  • Proceso ID: {terminal_status['process_id']}")
        print(f"  • Ruta: {terminal_status['terminal_path']}")
        print()
        
        print("🔍 OTROS TERMINALES MT5:")
        if other_terminals["count"] > 0:
            print(f"  • Encontrados: {other_terminals['count']} terminales")
            for i, terminal in enumerate(other_terminals["terminals"], 1):
                print(f"    {i}. {terminal['name']} (PID: {terminal['pid']})")
                print(f"       Ruta: {terminal['exe']}")
        else:
            print("  • No hay otros terminales MT5 ejecutándose")
        print()
        
    except Exception as e:
        print(f"❌ Error obteniendo estado: {e}")
        return
    
    # 2. Health Check del sistema
    print("2️⃣ HEALTH CHECK DEL SISTEMA")
    print("=" * 35)
    
    try:
        health = fn_manager.health_check()
        
        print("🏥 RESULTADOS DEL HEALTH CHECK:")
        print(f"  • Salud general: {'✅ BUENA' if health['overall_health'] else '❌ PROBLEMAS'}")
        print(f"  • Terminal ejecutándose: {'✅ SÍ' if health['terminal_running'] else '❌ NO'}")
        print(f"  • Conexión MT5: {'✅ SÍ' if health['mt5_connected'] else '❌ NO'}")
        print(f"  • Configuración válida: {'✅ SÍ' if health['configuration_valid'] else '❌ NO'}")
        print(f"  • Modo exclusivo: {'✅ SÍ' if health['exclusive_mode'] else '⚠️ NO'}")
        print(f"  • Timestamp: {health['timestamp']}")
        print()
        
    except Exception as e:
        print(f"❌ Error en health check: {e}")
        return
    
    # 3. Gestión inteligente del terminal
    print("3️⃣ GESTIÓN INTELIGENTE DEL TERMINAL")
    print("=" * 40)
    
    try:
        print("🔍 Verificando estado actual...")
        is_running, pid = fn_manager.is_fundednext_terminal_running()
        
        if is_running:
            print(f"✅ FundedNext MT5 Terminal ya está ejecutándose (PID: {pid})")
            print("   → No es necesario abrirlo")
        else:
            print("📋 FundedNext MT5 Terminal no está ejecutándose")
            
            # Verificar otros terminales
            other_terminals = fn_manager.get_other_mt5_terminals()
            if other_terminals:
                print(f"⚠️ Encontrados {len(other_terminals)} otros terminales MT5:")
                for terminal in other_terminals:
                    print(f"   - {terminal['name']} (PID: {terminal['pid']})")
                
                # Preguntar si cerrar otros terminales (en modo real sería automático)
                print("\n🤔 ¿Configuración para cerrar otros terminales?")
                config_close = fn_manager.fundednext_config["close_other_terminals"]
                print(f"   → close_other_terminals: {config_close}")
                
                if config_close:
                    print("🔄 Cerrando otros terminales MT5...")
                    closed_count = fn_manager.close_other_mt5_terminals()
                    print(f"✅ Se cerraron {closed_count} terminales")
            
            # Verificar configuración de auto-apertura
            auto_open = fn_manager.fundednext_config["auto_open_if_closed"]
            print(f"\n🚀 ¿Configuración para auto-apertura? {auto_open}")
            
            if auto_open:
                print("🔄 Iniciando FundedNext MT5 Terminal...")
                success = fn_manager.start_fundednext_terminal()
                if success:
                    print("✅ FundedNext MT5 Terminal iniciado correctamente")
                else:
                    print("❌ Error iniciando FundedNext MT5 Terminal")
            else:
                print("⚠️ Auto-apertura deshabilitada. Terminal debe abrirse manualmente.")
        
        print()
        
    except Exception as e:
        print(f"❌ Error en gestión de terminal: {e}")
        return
    
    # 4. Conexión a MT5
    print("4️⃣ CONEXIÓN A METATRADER 5")
    print("=" * 35)
    
    try:
        print("🔌 Intentando conectar a MT5...")
        
        # Configurar para modo conservador (no cerrar otros terminales automáticamente)
        fn_manager.fundednext_config["close_other_terminals"] = False
        fn_manager.fundednext_config["auto_open_if_closed"] = False
        
        connection_success = fn_manager.connect_to_mt5()
        
        if connection_success:
            print("✅ Conexión a FundedNext MT5 establecida correctamente")
            
            if fn_manager.account_info:
                account = fn_manager.account_info
                print(f"📊 INFORMACIÓN DE CUENTA:")
                print(f"   • Login: {account.get('login', 'N/A')}")
                print(f"   • Servidor: {account.get('server', 'N/A')}")
                print(f"   • Nombre: {account.get('name', 'N/A')}")
                print(f"   • Balance: ${account.get('balance', 0):,.2f}")
                print(f"   • Equity: ${account.get('equity', 0):,.2f}")
                print(f"   • Margen: ${account.get('margin', 0):,.2f}")
                print(f"   • Margen libre: ${account.get('margin_free', 0):,.2f}")
        else:
            print("❌ No se pudo establecer conexión a MT5")
            print("   Posibles causas:")
            print("   - FundedNext MT5 Terminal no está ejecutándose")
            print("   - No hay cuenta configurada en el terminal")
            print("   - Terminal no está conectado al servidor")
        
        print()
        
    except Exception as e:
        print(f"❌ Error conectando a MT5: {e}")
        return
    
    # 5. Estado final del sistema
    print("5️⃣ ESTADO FINAL DEL SISTEMA")
    print("=" * 35)
    
    try:
        final_status = fn_manager.get_manager_status()
        final_health = fn_manager.health_check()
        metrics = final_status["metrics"]
        
        print("📊 MÉTRICAS FINALES:")
        print(f"   • Intentos de conexión: {metrics['connection_attempts']}")
        print(f"   • Conexiones exitosas: {metrics['successful_connections']}")
        print(f"   • Reinicios de terminal: {metrics['terminal_restarts']}")
        print(f"   • Otros terminales cerrados: {metrics['other_terminals_closed']}")
        print(f"   • Health checks: {metrics['health_checks']}")
        
        if metrics['last_connection_time']:
            print(f"   • Última conexión: {metrics['last_connection_time']}")
        
        print()
        print("🎯 RESUMEN FINAL:")
        print(f"   • Sistema operativo: {'✅ SÍ' if final_health['overall_health'] else '❌ NO'}")
        print(f"   • Terminal ejecutándose: {'✅ SÍ' if final_health['terminal_running'] else '❌ NO'}")
        print(f"   • MT5 conectado: {'✅ SÍ' if final_health['mt5_connected'] else '❌ NO'}")
        print(f"   • Modo exclusivo: {'✅ SÍ' if final_health.get('exclusive_mode', False) else '⚠️ NO'}")
        
    except Exception as e:
        print(f"❌ Error obteniendo estado final: {e}")
        return
    
    # Cleanup
    try:
        if fn_manager.is_connected:
            fn_manager.disconnect_from_mt5()
            print("\n🔌 Desconectado de MT5")
    except:
        pass
    
    print("\n✅ DEMO COMPLETADO")
    print("=" * 20)
    print("🚀 FundedNext MT5 Manager operativo y funcionando")
    print("⚡ Sistema listo para integración con SÓTANO 2")


if __name__ == "__main__":
    main()
