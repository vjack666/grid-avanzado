"""
🔍 VERIFICADOR DE CONEXIÓN MT5 - TRADING GRID
==========================================

Script para verificar qué archivo maneja MT5 y cómo está conectado

OBJETIVO: Encontrar el encargado de la conexión MT5
RESULTADO: Mostrar datos de la cuenta actual

FECHA: 2025-08-13
"""

import sys
import os
sys.path.append('.')

def test_current_mt5_connection():
    """🔍 Probar conexión MT5 actual"""
    print("🔍 Verificando conexión MT5 actual...")
    print("=" * 50)
    
    try:
        # Probar con FundedNext Manager
        print("📋 Probando FundedNext MT5 Manager...")
        from src.core.fundednext_mt5_manager import FundedNextMT5Manager
        from src.core.config_manager import ConfigManager
        from src.core.logger_manager import LoggerManager
        from src.core.error_manager import ErrorManager
        
        config = ConfigManager()
        logger = LoggerManager()
        error = ErrorManager(config, logger)
        mt5_mgr = FundedNextMT5Manager(config, logger, error)
        
        print(f"📊 Status inicial: {mt5_mgr.status}")
        
        # Intentar conexión
        result = mt5_mgr.connect_to_mt5()
        print(f"🔌 Conexión: {'✅' if result else '❌'}")
        
        if result and mt5_mgr.account_info:
            print(f"🏦 Cuenta: {mt5_mgr.account_info.get('login', 'N/A')}")
            print(f"💰 Balance: ${mt5_mgr.account_info.get('balance', 0):.2f}")
            print(f"🏢 Broker: {mt5_mgr.account_info.get('company', 'N/A')}")
            print(f"🌍 Servidor: {mt5_mgr.account_info.get('server', 'N/A')}")
            print("✅ FundedNext MT5 Manager ES EL ENCARGADO")
        else:
            print("❌ FundedNext MT5 Manager no pudo conectar")
            
    except Exception as e:
        print(f"❌ Error con FundedNext Manager: {e}")
    
    print("\n" + "=" * 50)
    
    try:
        # Probar con MT5 directo
        print("📋 Probando MT5 directo...")
        import MetaTrader5 as mt5
        
        if mt5.initialize():
            account_info = mt5.account_info()
            if account_info:
                print(f"🏦 Cuenta: {account_info.login}")
                print(f"💰 Balance: ${account_info.balance:.2f}")
                print(f"🏢 Broker: {account_info.company}")
                print(f"🌍 Servidor: {account_info.server}")
                print("✅ MT5 DIRECTO FUNCIONA")
            else:
                print("❌ No se pudo obtener info de cuenta")
            mt5.shutdown()
        else:
            print("❌ No se pudo inicializar MT5")
            
    except Exception as e:
        print(f"❌ Error con MT5 directo: {e}")

if __name__ == "__main__":
    test_current_mt5_connection()
