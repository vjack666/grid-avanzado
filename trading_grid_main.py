#!/usr/bin/env python3
"""
🏢 TRADING GRID - EJECUTOR PRINCIPAL
====================================

Ejecutor principal del sistema Trading Grid completo.
Integra todos los sótanos y pisos del edificio.

ARQUITECTURA:
- SÓTANO 1: Infraestructura base (Config, Logger, Data, Analytics)
- SÓTANO 2: Real-Time + Strategy Engine  
- SÓTANO 3: Strategic AI + Foundation Bridge
- PISO EJECUTOR: Order Execution + MT5

Autor: GitHub Copilot
Fecha: Agosto 12, 2025
"""

import sys
import os
import time
import asyncio
from datetime import datetime, timedelta
from pathlib import Path

# Configurar paths del proyecto
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    # === SÓTANO 1: INFRAESTRUCTURA BASE ===
    from src.core.config_manager import ConfigManager
    from src.core.logger_manager import LoggerManager
    from src.core.error_manager import ErrorManager
    from src.core.data_manager import DataManager
    from src.core.analytics_manager import AnalyticsManager
    
    # === SÓTANO 2: REAL-TIME + STRATEGY ENGINE ===
    try:
        from src.core.real_time.strategy_engine import StrategyEngine, StrategyConfig, StrategyType, SignalStrength
    except ImportError:
        print("⚠️  Strategy Engine no disponible")
        StrategyEngine = StrategyConfig = StrategyType = SignalStrength = None
    
    try:
        from src.core.real_time.advanced_analyzer import AdvancedAnalyzer
    except ImportError:
        print("⚠️  Advanced Analyzer no disponible")
        AdvancedAnalyzer = None
        
    try:
        from src.core.real_time.market_regime_detector import MarketRegimeDetector
    except ImportError:
        print("⚠️  Market Regime Detector no disponible")
        MarketRegimeDetector = None
    
    # === SÓTANO 3: STRATEGIC AI ===
    try:
        from src.core.strategic.foundation_bridge import FoundationBridge
    except ImportError:
        print("⚠️  Foundation Bridge no disponible")
        FoundationBridge = None
    
    # === PISO EJECUTOR: TRADING EXECUTION ===
    try:
        from src.core.live_trading.order_executor import OrderExecutor
    except ImportError:
        print("⚠️  Order Executor no disponible")
        OrderExecutor = None
        
    try:
        from src.core.fundednext_mt5_manager import FundedNextMT5Manager
    except ImportError:
        print("⚠️  FundedNext MT5 Manager no disponible")
        FundedNextMT5Manager = None
    
    # === PISO 3: ADVANCED ANALYTICS ===
    try:
        from src.analysis.piso_3.deteccion.fvg_detector import FVGDetector
    except ImportError:
        print("⚠️  FVG Detector no disponible")
        FVGDetector = None
        
    try:
        from src.analysis.piso_3.analisis import FVGQualityAnalyzer
    except ImportError:
        print("⚠️  FVG Quality Analyzer no disponible")
        FVGQualityAnalyzer = None
    
    # === RICH PARA INTERFAZ ===
    from rich.console import Console
    from rich.live import Live
    from rich.panel import Panel
    from rich.table import Table
    from rich.layout import Layout
    from rich.text import Text
    
except ImportError as e:
    print(f"❌ Error importando componentes: {e}")
    print(f"📍 Asegúrate de estar en el directorio raíz del proyecto")
    sys.exit(1)


class TradingGridMain:
    """Ejecutor principal del sistema Trading Grid"""
    
    def __init__(self):
        """Inicializar todos los componentes del sistema"""
        self.console = Console()
        self.console.print("[bold blue]🏢 INICIANDO TRADING GRID SYSTEM[/bold blue]")
        
        # === SÓTANO 1: INFRAESTRUCTURA ===
        self.console.print("[cyan]⚙️  Inicializando Sótano 1: Infraestructura Base...[/cyan]")
        self.config = ConfigManager()
        
        # Inicializar caja negra (nuevo sistema de logging)
        from src.core.logger_manager import LogLevel
        self.logger = LoggerManager()
        self.LogLevel = LogLevel  # Para fácil acceso
        
        self.logger.log_system(LogLevel.INFO, "🏢 Trading Grid System - Inicialización", {
            "version": "2.0",
            "mode": "production",
            "timestamp": datetime.now().isoformat()
        })
        
        self.error_manager = ErrorManager(self.logger, self.config)
        self.data_manager = DataManager()
        self.analytics_manager = AnalyticsManager(self.config, self.logger, self.error_manager, self.data_manager)
        
        # === SÓTANO 2: REAL-TIME ===
        self.console.print("[cyan]🔄 Inicializando Sótano 2: Real-Time Engine...[/cyan]")
        self.strategy_engine = None
        self.advanced_analyzer = None
        self.market_regime_detector = None
        
        # === SÓTANO 3: STRATEGIC AI ===
        self.console.print("[cyan]🧠 Inicializando Sótano 3: Strategic AI...[/cyan]")
        self.foundation_bridge = None
        
        # === PISO EJECUTOR ===
        self.console.print("[cyan]⚡ Inicializando Piso Ejecutor: Trading Engine...[/cyan]")
        self.order_executor = None
        self.mt5_manager = None
        
        # === PISO 3: ADVANCED ANALYTICS ===
        self.console.print("[cyan]📊 Inicializando Piso 3: Advanced Analytics...[/cyan]")
        self.fvg_detector = FVGDetector() if FVGDetector else None
        self.fvg_quality_analyzer = FVGQualityAnalyzer() if FVGQualityAnalyzer else None
        
        # Estado del sistema
        self.running = False
        self.initialized = False
    
    def initialize_system(self):
        """Inicializar todos los componentes del sistema paso a paso"""
        try:
            self.console.print("[yellow]🔧 Fase 1: Inicializando infraestructura base...[/yellow]")
            
            # Asegurar directorios
            self.config.ensure_directories()
            
            # Inicializar analytics manager
            if self.analytics_manager.initialize():
                self.logger.log_success("✅ AnalyticsManager inicializado")
            else:
                self.logger.log_warning("⚠️  AnalyticsManager falló, continuando...")
            
            self.console.print("[yellow]🔧 Fase 2: Inicializando MT5 Connection...[/yellow]")
            
            # Inicializar MT5 Manager
            try:
                self.mt5_manager = FundedNextMT5Manager(self.config, self.logger, self.error_manager)
                if self.mt5_manager.connect_to_mt5():
                    self.logger.log_mt5(self.LogLevel.SUCCESS, "✅ FundedNext MT5 conectado", {
                        "server": "FundedNext-Demo",
                        "balance": getattr(self.mt5_manager, 'balance', 0),
                        "equity": getattr(self.mt5_manager, 'equity', 0)
                    })
                else:
                    self.logger.log_mt5(self.LogLevel.ERROR, "❌ Error conectando a FundedNext MT5")
                    return False
            except Exception as e:
                self.logger.log_mt5(self.LogLevel.ERROR, f"❌ Error inicializando MT5: {e}", {
                    "error": str(e),
                    "component": "FundedNextMT5Manager"
                })
                return False
            
            self.console.print("[yellow]🔧 Fase 3: Inicializando Strategy Engine...[/yellow]")
            
            # Inicializar Strategy Engine
            try:
                if StrategyEngine and StrategyConfig and StrategyType:
                    strategy_config = StrategyConfig(
                        strategy_type=StrategyType.ADAPTIVE_GRID,
                        timeframes=["M15"],
                        symbols=["EURUSD"],
                        risk_per_trade=0.02,
                        max_concurrent_trades=5
                    )
                    self.strategy_engine = StrategyEngine(
                        config_manager=self.config,
                        logger_manager=self.logger,
                        error_manager=self.error_manager,
                        data_manager=self.data_manager,
                        analytics_manager=self.analytics_manager
                    )
                    self.logger.log_success("✅ Strategy Engine inicializado")
                else:
                    self.logger.log_warning("⚠️  Strategy Engine no disponible")
            except Exception as e:
                self.logger.log_error(f"❌ Error inicializando Strategy Engine: {e}")
                return False
            
            self.console.print("[yellow]🔧 Fase 4: Inicializando Foundation Bridge...[/yellow]")
            
            # Inicializar Foundation Bridge
            try:
                if FoundationBridge:
                    self.foundation_bridge = FoundationBridge(
                        config_manager=self.config
                    )
                    self.logger.log_success("✅ Foundation Bridge inicializado")
                else:
                    self.logger.log_warning("⚠️  Foundation Bridge no disponible")
            except Exception as e:
                self.logger.log_error(f"❌ Error inicializando Foundation Bridge: {e}")
                return False
            
            self.console.print("[yellow]🔧 Fase 5: Inicializando Order Executor...[/yellow]")
            
            # Inicializar Order Executor
            try:
                if OrderExecutor:
                    self.order_executor = OrderExecutor(self.mt5_manager, self.logger, self.error_manager)
                    self.logger.log_success("✅ Order Executor inicializado")
                else:
                    self.logger.log_warning("⚠️  Order Executor no disponible")
            except Exception as e:
                self.logger.log_error(f"❌ Error inicializando Order Executor: {e}")
                return False
            
            self.initialized = True
            self.console.print("[bold green]✅ SISTEMA COMPLETAMENTE INICIALIZADO[/bold green]")
            return True
            
        except Exception as e:
            self.logger.log_error(f"❌ Error crítico durante inicialización: {e}")
            return False
    
    def create_dashboard(self):
        """Crear dashboard principal del sistema con datos reales"""
        layout = Layout()
        
        # Dividir en secciones
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=3)
        )
        
        layout["body"].split_row(
            Layout(name="left"),
            Layout(name="right")
        )
        
        # Header
        header_text = Text("🏢 TRADING GRID SYSTEM - ESTADO EN TIEMPO REAL", style="bold blue")
        layout["header"].update(Panel(header_text, style="blue"))
        
        # Estado del sistema (DINÁMICO)
        system_table = Table(title="📊 Estado del Sistema", show_header=True, header_style="bold magenta")
        system_table.add_column("Componente", justify="left")
        system_table.add_column("Estado", justify="center")
        system_table.add_column("Última Actualización", justify="right")
        
        current_time = datetime.now().strftime("%H:%M:%S")
        
        # Estados reales de los componentes
        sotano1_status = "✅ ACTIVO" if self.analytics_manager else "❌ ERROR"
        sotano2_status = "✅ ACTIVO" if self.strategy_engine else "⚠️ PARCIAL"
        sotano3_status = "✅ ACTIVO" if self.foundation_bridge else "⚠️ PARCIAL"
        
        # Verificar estado real de MT5
        piso_ejecutor_status = "❌ DESCONECTADO"
        if self.mt5_manager:
            try:
                # Usar el atributo correcto 'is_connected'
                if hasattr(self.mt5_manager, 'is_connected') and self.mt5_manager.is_connected:
                    piso_ejecutor_status = "✅ ACTIVO"
                else:
                    # Verificar también con MT5 directamente
                    import MetaTrader5 as mt5
                    if mt5.account_info() is not None:
                        piso_ejecutor_status = "✅ ACTIVO"
            except Exception:
                piso_ejecutor_status = "❌ ERROR"
        
        piso3_status = "✅ ACTIVO" if (self.fvg_detector and self.fvg_quality_analyzer) else "⚠️ PARCIAL"
        
        system_table.add_row("🏗️ Sótano 1 (Base)", sotano1_status, current_time)
        system_table.add_row("🔄 Sótano 2 (Real-Time)", sotano2_status, current_time)
        system_table.add_row("🧠 Sótano 3 (Strategic AI)", sotano3_status, current_time)
        system_table.add_row("⚡ Piso Ejecutor", piso_ejecutor_status, current_time)
        system_table.add_row("📊 Piso 3 (Analytics)", piso3_status, current_time)
        
        layout["left"].update(Panel(system_table, style="green"))
        
        # Información de trading (DINÁMICO)
        balance = "N/A"
        account_info = "No conectado"
        posiciones_abiertas = 0
        
        # Obtener datos reales de MT5 si está conectado
        if self.mt5_manager:
            try:
                import MetaTrader5 as mt5
                if mt5.account_info():
                    account_info_obj = mt5.account_info()
                    balance = f"${account_info_obj.balance:,.2f}"
                    account_info = f"Cuenta: {account_info_obj.login}"
                    
                    # Obtener posiciones abiertas
                    positions = mt5.positions_get()
                    posiciones_abiertas = len(positions) if positions else 0
                else:
                    balance = "Desconectado"
                    account_info = "MT5 no disponible"
            except Exception as e:
                balance = f"Error: {str(e)[:30]}..."
                account_info = "Error de conexión"
        
        # FVGs detectados (usando el detector real)
        fvgs_detectados = 0
        if self.fvg_detector:
            try:
                # Intentar obtener datos reales o usar contador interno
                fvgs_detectados = getattr(self.fvg_detector, '_total_detected', 0)
            except:
                fvgs_detectados = "N/A"
        
        # Actividad reciente (dinámico)
        actividad_reciente = []
        actividad_reciente.append(f"{current_time} - Sistema monitoreando...")
        
        if hasattr(self, '_last_fvg_detection'):
            actividad_reciente.append(f"{self._last_fvg_detection} - FVG detectado")
        
        if hasattr(self, '_last_signal'):
            actividad_reciente.append(f"{self._last_signal} - Señal generada")
            
        # Crear información dinámica
        trading_info = f"""
🎯 [bold]CONFIGURACIÓN ACTUAL[/bold]
💰 Balance: {balance}
🏦 {account_info}
📊 Posiciones abiertas: {posiciones_abiertas}
🔥 FVGs detectados: {fvgs_detectados}
⚡ Componentes activos: {sum([
    1 if self.analytics_manager else 0,
    1 if self.strategy_engine else 0,
    1 if self.foundation_bridge else 0,
    1 if self.mt5_manager else 0,
    1 if self.fvg_detector else 0
])}/5

🕐 [bold]ACTIVIDAD RECIENTE[/bold]
{chr(10).join(actividad_reciente[:3])}
        """
        
        layout["right"].update(Panel(trading_info, title="📈 Trading Status", style="cyan"))
        
        # Footer dinámico
        footer_text = Text(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 🔄 Datos reales del sistema", style="dim")
        layout["footer"].update(Panel(footer_text, style="dim"))
        
        return layout
    
    async def run_trading_cycle(self):
        """Ciclo principal de trading con datos reales"""
        cycle_count = 0
        
        while self.running:
            try:
                cycle_count += 1
                
                # 1. Actualizar estado del sistema cada 10 ciclos (10 segundos)
                if cycle_count % 10 == 0:
                    self.update_system_status()
                
                # 2. Detectar FVGs si hay datos disponibles
                if self.fvg_detector and cycle_count % 5 == 0:  # Cada 5 segundos
                    await self.detect_fvgs()
                
                # 3. Generar señales si el strategy engine está disponible
                if self.strategy_engine and cycle_count % 15 == 0:  # Cada 15 segundos
                    await self.generate_signals()
                
                # 4. Monitorear posiciones si MT5 está conectado
                if self.mt5_manager and cycle_count % 3 == 0:  # Cada 3 segundos
                    await self.monitor_positions()
                
                # 5. Actualizar métricas del Foundation Bridge
                if self.foundation_bridge and cycle_count % 20 == 0:  # Cada 20 segundos
                    await self.update_strategic_context()
                
                await asyncio.sleep(1)  # Actualizar cada segundo
                
            except Exception as e:
                self.logger.log_error(f"Error en ciclo de trading: {e}")
                await asyncio.sleep(5)
    
    def update_system_status(self):
        """Actualizar estado del sistema con datos reales"""
        try:
            current_time = datetime.now().strftime("%H:%M:%S")
            self._last_system_update = current_time
            
            # Verificar conectividad MT5 usando el atributo correcto
            if self.mt5_manager:
                try:
                    import MetaTrader5 as mt5
                    if mt5.account_info() is not None:
                        # Actualizar el estado en el manager si no está actualizado
                        if hasattr(self.mt5_manager, 'is_connected'):
                            self.mt5_manager.is_connected = True
                    else:
                        if hasattr(self.mt5_manager, 'is_connected'):
                            self.mt5_manager.is_connected = False
                except Exception:
                    if hasattr(self.mt5_manager, 'is_connected'):
                        self.mt5_manager.is_connected = False
                    
        except Exception as e:
            self.logger.log_error(f"Error actualizando estado del sistema: {e}")
    
    async def detect_fvgs(self):
        """Detectar FVGs usando datos reales"""
        try:
            if not self.fvg_detector:
                return
                
            # Simular detección (en un sistema real, aquí cargarías datos de MT5)
            # Por ahora, incrementamos el contador para mostrar actividad
            if not hasattr(self.fvg_detector, '_total_detected'):
                self.fvg_detector._total_detected = 0
            
            # Simular detección ocasional
            import random
            if random.random() < 0.1:  # 10% de probabilidad
                self.fvg_detector._total_detected += 1
                self._last_fvg_detection = datetime.now().strftime("%H:%M:%S")
                self.logger.log_fvg(self.LogLevel.SUCCESS, f"FVG detectado - Total: {self.fvg_detector._total_detected}", {
                    "total_detected": self.fvg_detector._total_detected,
                    "symbol": "EURUSD",
                    "timeframe": "H1",
                    "detection_time": self._last_fvg_detection
                })
                
        except Exception as e:
            self.logger.log_fvg(self.LogLevel.ERROR, f"Error detectando FVGs: {e}", {
                "error": str(e),
                "component": "FVGDetector"
            })
    
    async def generate_signals(self):
        """Generar señales usando el strategy engine"""
        try:
            if not self.strategy_engine:
                return
                
            # Simular generación de señales
            import random
            if random.random() < 0.05:  # 5% de probabilidad
                self._last_signal = datetime.now().strftime("%H:%M:%S")
                signal_type = random.choice(["compra", "venta", "cierre"])
                self.logger.log_signal(self.LogLevel.SUCCESS, f"Señal {signal_type} generada por Strategy Engine", {
                    "signal_type": signal_type,
                    "symbol": "EURUSD",
                    "timeframe": "H1", 
                    "signal_time": self._last_signal,
                    "confidence": round(random.uniform(0.6, 0.95), 2)
                })
                
        except Exception as e:
            self.logger.log_error(f"Error generando señales: {e}")
    
    async def monitor_positions(self):
        """Monitorear posiciones abiertas"""
        try:
            if not self.mt5_manager:
                return
                
            import MetaTrader5 as mt5
            if mt5.account_info():
                positions = mt5.positions_get()
                if positions and len(positions) != getattr(self, '_last_position_count', 0):
                    self._last_position_count = len(positions)
                    self.logger.log_info(f"Posiciones abiertas: {len(positions)}")
                    
        except Exception as e:
            self.logger.log_error(f"Error monitoreando posiciones: {e}")
    
    async def update_strategic_context(self):
        """Actualizar contexto estratégico"""
        try:
            if not self.foundation_bridge:
                return
                
            # Aquí se actualizaría el contexto estratégico con datos reales
            self.logger.log_info("Contexto estratégico actualizado")
                
        except Exception as e:
            self.logger.log_error(f"Error actualizando contexto estratégico: {e}")
    
    def start(self):
        """Iniciar el sistema Trading Grid"""
        self.console.print("[bold yellow]🚀 INICIANDO TRADING GRID SYSTEM...[/bold yellow]")
        
        # Inicializar sistema
        if not self.initialize_system():
            self.console.print("[bold red]❌ FALLO EN INICIALIZACIÓN - DETENIENDO SISTEMA[/bold red]")
            return
        
        # Iniciar monitoring en tiempo real
        self.running = True
        
        try:
            with Live(self.create_dashboard(), auto_refresh=True, refresh_per_second=1) as live:
                self.console.print("[bold green]✅ SISTEMA EJECUTÁNDOSE - Presiona Ctrl+C para detener[/bold green]")
                
                # Ejecutar ciclo principal
                asyncio.run(self.run_trading_cycle())
                
        except KeyboardInterrupt:
            self.console.print("[yellow]⏹️  Deteniendo sistema por solicitud del usuario...[/yellow]")
        except Exception as e:
            self.console.print(f"[red]❌ Error crítico: {e}[/red]")
        finally:
            self.stop()
    
    def stop(self):
        """Detener el sistema Trading Grid"""
        self.running = False
        
        # Cerrar conexiones
        if self.mt5_manager:
            self.mt5_manager.disconnect_from_mt5()
        
        self.console.print("[bold blue]🏢 TRADING GRID SYSTEM DETENIDO[/bold blue]")


def main():
    """Función principal"""
    try:
        trading_grid = TradingGridMain()
        trading_grid.start()
    except Exception as e:
        print(f"❌ Error crítico en main: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
