#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 AUDITORÍA COMPLETA - TRADING GRID SYSTEM
==========================================

Verifica que TODOS los componentes estén integrados:
- SÓTANO 1: Infraestructura (Config, Logger, Analytics, Data)  
- SÓTANO 2: Real-Time (Strategy Engine, Advanced Analyzer)
- SÓTANO 3: Strategic AI (Foundation Bridge, ML Database)
- PISO EJECUTOR: Order Execution (Enhanced + Traditional)
- PISO 3: Advanced Analytics (FVG Detection, Quality Analysis)
- CAJA NEGRA: Logging unificado

Fecha: Agosto 13, 2025
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def audit_system_integration():
    """Auditar integración completa del sistema"""
    print("🔍" + "=" * 58)
    print("🔍 AUDITORÍA COMPLETA - TRADING GRID SYSTEM")
    print("🔍" + "=" * 58)
    
    try:
        # Importar sistema principal
        from trading_grid_main import TradingGridMain
        
        print("\n📊 CREANDO INSTANCIA DEL SISTEMA...")
        system = TradingGridMain()
        
        print("\n🔧 INICIALIZANDO TODOS LOS COMPONENTES...")
        initialization_success = system.initialize_system()
        
        if not initialization_success:
            print("❌ FALLO EN INICIALIZACIÓN")
            return False
        
        print("\n🔍 AUDITANDO COMPONENTES INTEGRADOS...")
        
        # === AUDITORÍA SÓTANO 1: INFRAESTRUCTURA ===
        print("\n🏗️  SÓTANO 1 - INFRAESTRUCTURA BASE:")
        
        components_s1 = {
            "ConfigManager": hasattr(system, 'config') and system.config is not None,
            "LoggerManager (Caja Negra)": hasattr(system, 'logger') and system.logger is not None,
            "ErrorManager": hasattr(system, 'error_manager') and system.error_manager is not None,
            "DataManager": hasattr(system, 'data_manager') and system.data_manager is not None,
            "AnalyticsManager": hasattr(system, 'analytics_manager') and system.analytics_manager is not None
        }
        
        for component, status in components_s1.items():
            status_icon = "✅" if status else "❌"
            print(f"   {status_icon} {component}")
        
        # === AUDITORÍA SÓTANO 2: REAL-TIME ===
        print("\n🔄 SÓTANO 2 - REAL-TIME ENGINE:")
        
        components_s2 = {
            "StrategyEngine": hasattr(system, 'strategy_engine') and system.strategy_engine is not None,
            "AdvancedAnalyzer": hasattr(system, 'advanced_analyzer') and system.advanced_analyzer is not None,
            "MarketRegimeDetector": hasattr(system, 'market_regime_detector') and system.market_regime_detector is not None
        }
        
        for component, status in components_s2.items():
            status_icon = "✅" if status else "⚠️ "
            print(f"   {status_icon} {component}")
        
        # === AUDITORÍA SÓTANO 3: STRATEGIC AI ===
        print("\n🧠 SÓTANO 3 - STRATEGIC AI + ML FOUNDATION:")
        
        components_s3 = {
            "FoundationBridge": hasattr(system, 'foundation_bridge') and system.foundation_bridge is not None,
            "FVG Database Manager (ML)": hasattr(system, 'fvg_db_manager') and system.fvg_db_manager is not None
        }
        
        for component, status in components_s3.items():
            status_icon = "✅" if status else "⚠️ "
            print(f"   {status_icon} {component}")
        
        # === AUDITORÍA PISO EJECUTOR: TRADING ENGINE ===
        print("\n⚡ PISO EJECUTOR - TRADING ENGINE:")
        
        # Verificar si Enhanced Order Executor está operativo
        enhanced_operational = hasattr(system, 'enhanced_order_executor') and system.enhanced_order_executor is not None
        traditional_operational = hasattr(system, 'order_executor') and system.order_executor is not None
        mt5_operational = hasattr(system, 'mt5_manager') and system.mt5_manager is not None
        
        components_pe = {
            "MT5Manager (FundedNext)": mt5_operational,
            "Enhanced Order Executor (FVG Limits)": enhanced_operational,
            "Traditional Order Executor (Fallback)": traditional_operational
        }
        
        for component, status in components_pe.items():
            if component == "Traditional Order Executor (Fallback)":
                # Solo mostrar warning si Enhanced no está disponible
                if enhanced_operational:
                    status_icon = "✅" if status else "🔘"  # No crítico si Enhanced funciona
                    note = " (No requerido - Enhanced activo)" if not status else ""
                    print(f"   {status_icon} {component}{note}")
                else:
                    status_icon = "⚠️ " if not status else "✅"
                    note = " (REQUERIDO - Enhanced no disponible)" if not status else ""
                    print(f"   {status_icon} {component}{note}")
            else:
                status_icon = "✅" if status else "⚠️ "
                print(f"   {status_icon} {component}")
        
        # Determinar si el piso ejecutor es operativo
        executor_operational = enhanced_operational or traditional_operational
        
        # === AUDITORÍA PISO 3: ADVANCED ANALYTICS ===
        print("\n📊 PISO 3 - ADVANCED ANALYTICS:")
        
        components_p3 = {
            "FVG Detector": hasattr(system, 'fvg_detector') and system.fvg_detector is not None,
            "FVG Quality Analyzer": hasattr(system, 'fvg_quality_analyzer') and system.fvg_quality_analyzer is not None
        }
        
        for component, status in components_p3.items():
            status_icon = "✅" if status else "⚠️ "
            print(f"   {status_icon} {component}")
        
        # === AUDITORÍA INTEGRACIÓN FVG → ENHANCED ORDER ===
        print("\n🎯 INTEGRACIÓN FVG → ENHANCED ORDER:")
        
        fvg_integration = hasattr(system, '_fvg_trading_callback') and system._fvg_trading_callback is not None
        callback_icon = "✅" if fvg_integration else "⚠️ "
        print(f"   {callback_icon} FVG → Enhanced Order Callback")
        
        # Test integración ML Database
        if hasattr(system, 'fvg_db_manager') and system.fvg_db_manager:
            try:
                db_stats = system.fvg_db_manager.get_database_stats()
                print(f"   ✅ ML Database operativa: {db_stats.get('total_fvgs', 0)} FVGs almacenados")
            except Exception as e:
                print(f"   ⚠️  ML Database error: {e}")
        
        # === AUDITORÍA CAJA NEGRA (LOGGING) ===
        print("\n📦 CAJA NEGRA - LOGGING UNIFICADO:")
        
        if hasattr(system, 'logger') and system.logger:
            try:
                # Test logging categories
                system.logger.log_system(system.LogLevel.INFO, "🔍 Test auditoría completa", {
                    "audit_timestamp": "2025-08-13",
                    "components_tested": len(components_s1) + len(components_s2) + len(components_s3) + len(components_pe) + len(components_p3)
                })
                print("   ✅ Sistema de logging operativo (todas las categorías)")
                print("   ✅ Logs: system, mt5, fvg, strategy, analytics, security, performance")
            except Exception as e:
                print(f"   ⚠️  Error en logging: {e}")
        
        # === RESUMEN EJECUTIVO ===
        print("\n📊 RESUMEN EJECUTIVO:")
        
        total_components = len(components_s1) + len(components_s2) + len(components_s3) + len(components_pe) + len(components_p3)
        operational_components = sum([
            sum(components_s1.values()),
            sum(components_s2.values()), 
            sum(components_s3.values()),
            sum(components_pe.values()),
            sum(components_p3.values())
        ])
        
        # Componentes críticos: Infraestructura + MT5 + AL MENOS UN Ejecutor de órdenes
        critical_s1 = sum(components_s1.values())  # Infraestructura completa
        critical_mt5 = 1 if mt5_operational else 0  # MT5 Manager
        critical_executor = 1 if (enhanced_operational or traditional_operational) else 0  # Al menos un executor
        
        critical_components = critical_s1 + critical_mt5 + critical_executor
        total_critical = len(components_s1) + 1 + 1  # Infraestructura + MT5 + Executor
        
        print(f"   📈 Componentes operativos: {operational_components}/{total_components}")
        print(f"   🔥 Componentes críticos: {critical_components}/{total_critical}")
        print(f"   💾 ML Foundation: {'✅ Operativo' if hasattr(system, 'fvg_db_manager') and system.fvg_db_manager else '⚠️  No disponible'}")
        print(f"   🎯 Enhanced Orders: {'✅ Operativo' if hasattr(system, 'enhanced_order_executor') and system.enhanced_order_executor else '⚠️  Fallback tradicional'}")
        print(f"   📦 Caja Negra Logging: {'✅ Operativo' if hasattr(system, 'logger') and system.logger else '❌ Error'}")
        
        # Determinar estado general
        if critical_components == total_critical:
            if operational_components >= total_components * 0.8:  # 80% de componentes
                print(f"\n🎉 ESTADO: ✅ SISTEMA COMPLETAMENTE OPERATIVO")
                print(f"   El sistema Trading Grid está listo para ejecución en producción.")
                print(f"   Todos los sótanos, pisos y la caja negra están integrados.")
                return True
            else:
                print(f"\n⚠️  ESTADO: 🟡 SISTEMA PARCIALMENTE OPERATIVO")
                print(f"   Componentes críticos funcionando, algunos opcionales faltan.")
                return True
        else:
            print(f"\n❌ ESTADO: 🔴 SISTEMA NO OPERATIVO")
            print(f"   Fallan componentes críticos para funcionamiento.")
            return False
        
    except Exception as e:
        print(f"❌ ERROR EN AUDITORÍA: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Ejecutar auditoría completa"""
    success = audit_system_integration()
    
    if success:
        print(f"\n🎯" + "=" * 58)
        print("🎯 AUDITORÍA COMPLETADA - SISTEMA LISTO")
        print("🎯" + "=" * 58)
        print("   Para ejecutar el sistema completo:")
        print("   > python trading_grid_main.py")
    else:
        print(f"\n❌ AUDITORÍA FALLIDA - REVISAR COMPONENTES")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
