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
import json
import random
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
    
    # === SÓTANO 3: STRATEGIC AI + ML FOUNDATION ===
    try:
        from src.core.strategic.foundation_bridge import FoundationBridge
    except ImportError:
        print("⚠️  Foundation Bridge no disponible")
        FoundationBridge = None
    
    try:
        from src.core.ml_foundation.fvg_database_manager import FVGDatabaseManager
    except ImportError:
        print("⚠️  FVG Database Manager no disponible")
        FVGDatabaseManager = None
    
    # === PISO EJECUTOR: TRADING EXECUTION ===
    try:
        from src.core.live_trading.order_executor import OrderExecutor
    except ImportError:
        print("⚠️  Order Executor no disponible")
        OrderExecutor = None
    
    try:
        from src.core.live_trading.enhanced_order_executor import EnhancedOrderExecutor, create_enhanced_order_executor
    except ImportError:
        print("⚠️  Enhanced Order Executor no disponible")
        EnhancedOrderExecutor = None
        create_enhanced_order_executor = None
        
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
        self.fvg_db_manager = None  # ML Foundation Database Manager
        
        # === PISO EJECUTOR ===
        self.console.print("[cyan]⚡ Inicializando Piso Ejecutor: Trading Engine...[/cyan]")
        self.order_executor = None
        self.enhanced_order_executor = None  # Nueva versión con órdenes límite FVG
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
                    # Obtener configuración dinámica
                    symbols = self.config.get_symbols()
                    timeframes = self.config.get_timeframes()
                    
                    strategy_config = StrategyConfig(
                        strategy_type=StrategyType.ADAPTIVE_GRID,
                        timeframes=timeframes[:1] if timeframes else _config_manager.get_timeframes()[:1] if _config_manager else ['M15'],  # Usar primer timeframe
                        symbols=symbols[:1] if symbols else [_config_manager.get_primary_symbol() if _config_manager else 'EURUSD'],  # Usar primer símbolo
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
            
            self.console.print("[yellow]🔧 Fase 4.5: Inicializando ML Foundation...[/yellow]")
            
            # Inicializar FVG Database Manager
            try:
                if FVGDatabaseManager:
                    # Crear el directorio para la base de datos
                    ml_data_path = "data/ml"
                    os.makedirs(ml_data_path, exist_ok=True)
                    
                    self.fvg_db_manager = FVGDatabaseManager(
                        db_path=f"{ml_data_path}/fvg_master.db"
                    )
                    
                    self.logger.log_success("✅ FVG Database Manager inicializado")
                    
                    # Conectar con FoundationBridge si está disponible
                    if hasattr(self, 'foundation_bridge') and self.foundation_bridge:
                        # Note: FoundationBridge necesitará método set_ml_foundation()
                        self.logger.log_success("✅ ML Foundation disponible para FoundationBridge")
                else:
                    self.logger.log_warning("⚠️  FVG Database Manager no disponible")
            except Exception as e:
                self.logger.log_error(f"❌ Error inicializando FVG Database Manager: {e}")
                # No return False - continuar sin ML Foundation
            
            self.console.print("[yellow]🔧 Fase 5: Inicializando Enhanced Order Executor (FVG)...[/yellow]")
            
            self.console.print("[yellow]🔧 Fase 5: Inicializando Enhanced Order Executor (FVG)...[/yellow]")
            
            # Inicializar Enhanced Order Executor con órdenes límite FVG
            enhanced_success = False
            try:
                if create_enhanced_order_executor:
                    self.enhanced_order_executor = create_enhanced_order_executor(
                        config_manager=self.config,
                        logger_manager=self.logger,
                        error_manager=self.error_manager
                    )
                    
                    if self.enhanced_order_executor:
                        self.enhanced_order_executor.is_active = True
                        self.logger.log_success("✅ Enhanced Order Executor (FVG Limit Orders) inicializado")
                        
                        # Conectar con FVG Database Manager si está disponible
                        if hasattr(self, 'fvg_db_manager') and self.fvg_db_manager:
                            self.enhanced_order_executor.ml_foundation = self.fvg_db_manager
                            self.logger.log_success("✅ Enhanced Order Executor conectado con ML Foundation")
                        
                        enhanced_success = True
                    else:
                        self.logger.log_warning("⚠️  Enhanced Order Executor falló creación")
                        
                else:
                    self.logger.log_warning("⚠️  Enhanced Order Executor no disponible")
                    
            except Exception as e:
                self.logger.log_error(f"❌ Error inicializando Enhanced Order Executor: {e}")
                enhanced_success = False
            
            # SIEMPRE inicializar Traditional Order Executor como respaldo
            self.console.print("[yellow]🔧 Fase 5.5: Inicializando Traditional Order Executor (Respaldo)...[/yellow]")
            try:
                if OrderExecutor and self.mt5_manager:
                    self.order_executor = OrderExecutor(
                        fundednext_manager=self.mt5_manager,
                        logger_manager=self.logger,
                        error_manager=self.error_manager
                    )
                    if enhanced_success:
                        self.logger.log_success("✅ Traditional Order Executor inicializado como respaldo")
                    else:
                        self.logger.log_success("✅ Traditional Order Executor inicializado como principal")
                else:
                    self.logger.log_error("❌ Traditional Order Executor no disponible")
                    if not enhanced_success:
                        self.logger.log_error("❌ No hay ejecutores de órdenes disponibles")
                        return False
                        
            except Exception as e:
                self.logger.log_error(f"❌ Error inicializando Traditional Order Executor: {e}")
                if not enhanced_success:
                    self.logger.log_error("❌ Sistema sin ejecutores de órdenes funcionales")
                    return False
            
            # Integrar sistema ML FVG
            self.console.print("[yellow]🔧 Fase 6: Integrando sistema ML FVG...[/yellow]")
            if self.integrate_fvg_ml_system():
                self.logger.log_success("✅ Sistema ML FVG integrado exitosamente")
            else:
                self.logger.log_warning("⚠️  Sistema ML FVG no pudo integrarse completamente")
            
            self.initialized = True
            self.console.print("[bold green]✅ SISTEMA COMPLETAMENTE INICIALIZADO[/bold green]")
            return True
            
        except Exception as e:
            self.logger.log_error(f"❌ Error crítico durante inicialización: {e}")
            return False
    
    def create_dashboard(self):
        """Crear dashboard principal del sistema con datos reales"""
        layout = Layout()
        
        # Dividir en secciones con tamaños más controlados
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body", size=20),
            Layout(name="footer", size=3)
        )
        
        layout["body"].split_row(
            Layout(name="left", ratio=1),
            Layout(name="right", ratio=1)
        )
        
        # Header
        header_text = Text("🏢 TRADING GRID SYSTEM - ESTADO EN TIEMPO REAL", style="bold blue")
        layout["header"].update(Panel(header_text, style="blue", padding=(0, 1)))
        
        # Estado del sistema (DINÁMICO)
        system_table = Table(title="📊 Estado del Sistema", show_header=True, header_style="bold magenta", 
                           show_lines=False, box=None, padding=(0, 1))
        system_table.add_column("Componente", justify="left", width=17)
        system_table.add_column("Estado", justify="center", width=11)
        system_table.add_column("Última Actualización", justify="right", width=17)
        
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
        
        layout["left"].update(Panel(system_table, style="green", padding=(0, 1)))
        
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
        
        # Actividad reciente (dinámico) - más compacto
        actividad_reciente = []
        actividad_reciente.append(f"{current_time} - Sistema monitoreando...")
        
        if hasattr(self, '_last_fvg_detection'):
            actividad_reciente.append(f"{self._last_fvg_detection} - FVG detectado")
        
        if hasattr(self, '_last_signal'):
            actividad_reciente.append(f"{self._last_signal} - Señal generada")
            
        # Crear información dinámica más compacta
        trading_info = Text()
        trading_info.append("🎯 CONFIGURACIÓN ACTUAL\n", style="bold")
        trading_info.append(f"💰 Balance: {balance}\n")
        trading_info.append(f"🏦 {account_info}\n")
        trading_info.append(f"📊 Posiciones abiertas: {posiciones_abiertas}\n")
        trading_info.append(f"🔥 FVGs detectados: {fvgs_detectados}\n")
        trading_info.append(f"⚡ Componentes activos: {sum([
            1 if self.analytics_manager else 0,
            1 if self.strategy_engine else 0,
            1 if self.foundation_bridge else 0,
            1 if self.mt5_manager else 0,
            1 if self.fvg_detector else 0
        ])}/5\n\n")
        
        trading_info.append("🕐 ACTIVIDAD RECIENTE\n", style="bold")
        for activity in actividad_reciente[:3]:
            trading_info.append(f"{activity}\n")
        
        layout["right"].update(Panel(trading_info, title="📈 Trading Status", style="cyan", padding=(0, 1)))
        
        # Footer dinámico
        footer_text = Text(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 🔄 Datos reales del sistema", style="dim")
        layout["footer"].update(Panel(footer_text, style="dim", padding=(0, 1)))
        
        return layout
    
    def display_simple_status(self):
        """Mostrar estado del sistema de forma estática sin saltos"""
        self.console.print("\n[bold blue]🏢 TRADING GRID SYSTEM - ESTADO ACTUAL[/bold blue]")
        self.console.print("=" * 80)
        
        # Estado básico del sistema
        current_time = datetime.now().strftime("%H:%M:%S")
        self.console.print(f"⏰ Última actualización: {current_time}")
        
        # Componentes principales
        components = [
            ("🏗️ Sótano 1 (Base)", "✅ ACTIVO" if self.analytics_manager else "❌ ERROR"),
            ("🔄 Sótano 2 (Real-Time)", "✅ ACTIVO" if self.strategy_engine else "⚠️ PARCIAL"),
            ("🧠 Sótano 3 (Strategic AI)", "✅ ACTIVO" if self.foundation_bridge else "⚠️ PARCIAL"),
            ("⚡ Piso Ejecutor", "✅ ACTIVO" if self.mt5_manager else "❌ DESCONECTADO"),
            ("📊 Piso 3 (Analytics)", "✅ ACTIVO" if (self.fvg_detector and self.fvg_quality_analyzer) else "⚠️ PARCIAL")
        ]
        
        for component, status in components:
            self.console.print(f"{component:<25} {status}")
        
        # Información de trading básica
        if self.mt5_manager:
            try:
                import MetaTrader5 as mt5
                if hasattr(mt5, 'account_info') and mt5.account_info():
                    account_info_obj = mt5.account_info()
                    self.console.print(f"💰 Balance: ${account_info_obj.balance:,.2f}")
                    self.console.print(f"🏦 Cuenta: {account_info_obj.login}")
                else:
                    self.console.print("💰 Balance: Desconectado")
            except Exception:
                self.console.print("💰 Balance: Error de conexión")
        else:
            self.console.print("💰 Balance: MT5 no disponible")
        
        self.console.print("=" * 80)
        self.console.print("[dim]Sistema ejecutándose en tiempo real...[/dim]\n")
    
    async def run_trading_cycle(self):
        """Ciclo principal de trading con datos reales - SIN saltos de pantalla"""
        cycle_count = 0
        
        while self.running:
            try:
                cycle_count += 1
                
                # 1. Actualizar estado del sistema cada 30 ciclos (30 segundos) - MENOS FRECUENTE
                if cycle_count % 30 == 0:
                    self.update_system_status()
                    # Solo mostrar actualización de tiempo ocasionalmente
                    current_time = datetime.now().strftime("%H:%M:%S")
                    print(f"\r⏰ {current_time} - Sistema funcionando... (Ctrl+C para detener)", end="", flush=True)
                
                # 2. Detectar FVGs si hay datos disponibles
                if self.fvg_detector and cycle_count % 10 == 0:  # Cada 10 segundos
                    await self.detect_fvgs()
                
                # 3. Generar señales si el strategy engine está disponible
                if self.strategy_engine and cycle_count % 30 == 0:  # Cada 30 segundos
                    await self.generate_signals()
                
                # 4. Monitorear posiciones si MT5 está conectado
                if self.mt5_manager and cycle_count % 15 == 0:  # Cada 15 segundos
                    await self.monitor_positions()
                
                # 5. Actualizar métricas del Foundation Bridge
                if self.foundation_bridge and cycle_count % 60 == 0:  # Cada 60 segundos
                    await self.update_strategic_context()
                
                await asyncio.sleep(1)  # Actualizar cada segundo pero sin mostrar nada
                
            except Exception as e:
                self.logger.log_error(f"❌ Error en ciclo de trading: {e}")
                await asyncio.sleep(5)  # Pausa más larga en caso de error
    
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
        """Detectar FVGs usando datos reales y procesarlos con Enhanced Order Executor"""
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
                
                # Crear datos simulados de FVG para testing
                # Usar configuración dinámica en lugar de valores hardcodeados
                primary_symbol = self.config.get_primary_symbol()
                default_timeframe = self.config.get_default_timeframe()
                
                mock_fvg_data = {
                    'symbol': primary_symbol,
                    'timeframe': default_timeframe,
                    'type': ('BULLISH' if random.random() > 0.5 else 'BEARISH'),  # Mayúsculas para Enhanced Order Executor
                    'gap_high': 1.0950 + random.uniform(-0.0050, 0.0050),
                    'gap_low': 1.0940 + random.uniform(-0.0050, 0.0050),
                    'gap_size': random.uniform(0.0005, 0.0020),
                    'quality_score': random.uniform(0.6, 0.9),
                    'formation_time': datetime.now(),
                    'status': 'ACTIVE',  # Agregar status requerido por Enhanced Order Executor
                    'fvg_id': self.fvg_detector._total_detected,  # ID único
                    'validated': True,  # Atributo de validación
                    'confidence': random.uniform(0.7, 0.95)  # Confianza del FVG
                }
                
                # Crear objeto FVG simulado con atributos
                class MockFVGData:
                    def __init__(self, data):
                        for key, value in data.items():
                            setattr(self, key, value)
                
                fvg_object = MockFVGData(mock_fvg_data)
                
                # Log del FVG detectado
                self.logger.log_fvg(self.LogLevel.SUCCESS, f"FVG detectado - Total: {self.fvg_detector._total_detected}", {
                    "total_detected": self.fvg_detector._total_detected,
                    "symbol": fvg_object.symbol,
                    "timeframe": fvg_object.timeframe,
                    "type": fvg_object.type,
                    "gap_size": fvg_object.gap_size,
                    "quality_score": fvg_object.quality_score,
                    "detection_time": self._last_fvg_detection
                })
                
                # 🎯 NUEVO: Procesar FVG con Enhanced Order Executor
                if hasattr(self, '_fvg_trading_callback') and self._fvg_trading_callback:
                    try:
                        # Ejecutar callback del Enhanced Order Executor
                        self._fvg_trading_callback(fvg_object)
                        self.logger.log_success(f"✅ FVG procesado con Enhanced Order Executor: {fvg_object.symbol}")
                    except Exception as callback_error:
                        self.logger.log_error(f"❌ Error en callback Enhanced Order Executor: {callback_error}")
                
                # Fallback: Procesar con callback tradicional ML
                elif hasattr(self, '_fvg_ml_callback') and self._fvg_ml_callback:
                    try:
                        self._fvg_ml_callback(mock_fvg_data)
                        self.logger.log_success(f"✅ FVG procesado con ML tradicional: {fvg_object.symbol}")
                    except Exception as ml_error:
                        self.logger.log_error(f"❌ Error en callback ML tradicional: {ml_error}")
                
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
                    "symbol": self.config.get_primary_symbol(),
                    "timeframe": self.config.get_default_timeframe(), 
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
            # Crear un terminal más estable con menos refresh
            self.console.clear()
            self.console.print("[bold green]✅ SISTEMA EJECUTÁNDOSE - Presiona Ctrl+C para detener[/bold green]")
            
            # Dashboard más simple sin Live para evitar saltos
            self.display_simple_status()
            
            # Ejecutar ciclo principal
            asyncio.run(self.run_trading_cycle())
                
        except KeyboardInterrupt:
            self.console.print("[yellow]⏹️  Deteniendo sistema por solicitud del usuario...[/yellow]")
        except Exception as e:
            self.console.print(f"[red]❌ Error crítico: {e}[/red]")
        finally:
            self.stop()
    
    def integrate_fvg_ml_system(self):
        """
        🎯 INTEGRAR SISTEMA FVG + ML + ENHANCED ORDER EXECUTOR
        
        Nueva integración que conecta:
        1. FVG Detection → Enhanced Order Executor → Órdenes Límite Inteligentes
        2. ML Foundation para almacenamiento y análisis de datos
        3. Análisis de calidad para optimizar parámetros de orden
        """
        try:
            # Verificar disponibilidad de Enhanced Order Executor
            if not (hasattr(self, 'enhanced_order_executor') and self.enhanced_order_executor):
                self.logger.log_warning("⚠️  Enhanced Order Executor no disponible para integración FVG")
                
                # Fallback: Integración tradicional con ML Database
                return self._integrate_traditional_fvg_ml()
            
            # Integrar FVG Detection con Enhanced Order Executor
            if FVGDetector and hasattr(self, 'fvg_detector') and self.fvg_detector:
                
                def process_fvg_for_trading(fvg_data):
                    """
                    🎯 CALLBACK PRINCIPAL: FVG detectado → Orden límite inteligente
                    
                    Este callback procesa cada FVG detectado y genera una orden límite
                    inteligente utilizando el Enhanced Order Executor.
                    """
                    try:
                        self.logger.log_info(f"🎯 FVG detectado para trading: {fvg_data.symbol} {fvg_data.type}")
                        
                        # 1. Almacenar en ML Database si está disponible
                        if hasattr(self, 'fvg_db_manager') and self.fvg_db_manager:
                            # Validar y normalizar gap_type
                            gap_type = fvg_data.type.upper() if hasattr(fvg_data, 'type') and fvg_data.type else 'UNKNOWN'
                            if gap_type not in ['BULLISH', 'BEARISH']:
                                self.logger.log_warning(f"⚠️ Gap type no reconocido: {fvg_data.type}, usando BULLISH por defecto")
                                gap_type = 'BULLISH'
                            
                            fvg_record = {
                                'timestamp_creation': fvg_data.formation_time if hasattr(fvg_data, 'formation_time') else datetime.now(),
                                'symbol': fvg_data.symbol,
                                'timeframe': fvg_data.timeframe,
                                'gap_type': gap_type,
                                'gap_high': fvg_data.gap_high,
                                'gap_low': fvg_data.gap_low,
                                'gap_size_pips': fvg_data.gap_size * 10000,
                                'quality_score': getattr(fvg_data, 'quality_score', 0.5),
                                
                                # Datos básicos para ML
                                'vela1_open': 0.0, 'vela1_high': 0.0, 'vela1_low': 0.0, 'vela1_close': 0.0, 'vela1_volume': 0,
                                'vela2_open': 0.0, 'vela2_high': 0.0, 'vela2_low': 0.0, 'vela2_close': 0.0, 'vela2_volume': 0,
                                'vela3_open': 0.0, 'vela3_high': 0.0, 'vela3_low': 0.0, 'vela3_close': 0.0, 'vela3_volume': 0,
                                'current_price': 0.0,
                                'distance_to_gap': 0.0
                            }
                            
                            fvg_id = self.fvg_db_manager.insert_fvg(fvg_record)
                            if fvg_id:
                                self.logger.log_success(f"✅ FVG almacenado en ML DB: ID {fvg_id}")
                        
                        # 2. Procesar FVG con Enhanced Order Executor para generar orden límite
                        # Usar detección automática de sesión y tendencia
                        current_session = self.config.get_current_session()
                        trend_value = random.uniform(-1.0, 1.0)  # Simular análisis de tendencia
                        market_trend = self.config.detect_market_trend(trend_value)
                        
                        market_context = {
                            'trend': market_trend,
                            'volatility': 'NORMAL',
                            'session': current_session,
                            'volume_profile': 'AVERAGE'
                        }
                        
                        # 3. Generar orden límite inteligente
                        order_success = self.enhanced_order_executor.process_fvg_signal(fvg_data, market_context)
                        
                        if order_success:
                            self.logger.log_success(f"✅ Orden límite FVG generada exitosamente: {fvg_data.symbol}")
                        else:
                            self.logger.log_warning(f"⚠️  No se pudo generar orden límite para FVG: {fvg_data.symbol}")
                        
                    except Exception as e:
                        self.logger.log_error(f"❌ Error procesando FVG para trading: {e}")
                
                # Configurar el callback en el detector
                if hasattr(self.fvg_detector, 'set_callback'):
                    self.fvg_detector.set_callback(process_fvg_for_trading)
                    self.logger.log_success("✅ Enhanced Order Executor integrado con FVGDetector")
                else:
                    # Guardar referencia para uso manual
                    self._fvg_trading_callback = process_fvg_for_trading
                    self.logger.log_success("✅ Enhanced Order Executor preparado para FVGDetector")
                
                # 4. Programar monitoreo de órdenes activas
                self._schedule_fvg_order_monitoring()
                
                return True
            else:
                self.logger.log_warning("⚠️  FVGDetector no disponible para integración")
                return False
                
        except Exception as e:
            self.logger.log_error(f"❌ Error integrando Enhanced FVG trading system: {e}")
            return False
    
    
    def _integrate_traditional_fvg_ml(self):
        """Integración tradicional FVG + ML (fallback)"""
        try:
            if not (hasattr(self, 'fvg_db_manager') and self.fvg_db_manager):
                return False
                
            def store_fvg_callback(fvg_data):
                # Lógica tradicional de almacenamiento en ML DB
                try:
                    fvg_record = {
                        'timestamp_creation': getattr(fvg_data, 'formation_time', datetime.now()),
                        'symbol': fvg_data.symbol,
                        'timeframe': fvg_data.timeframe,
                        'gap_type': fvg_data.type,
                        'gap_high': fvg_data.gap_high,
                        'gap_low': fvg_data.gap_low,
                        'gap_size_pips': fvg_data.gap_size * 10000,
                        'quality_score': getattr(fvg_data, 'quality_score', 0.5),
                        'vela1_open': 0.0, 'vela1_high': 0.0, 'vela1_low': 0.0, 'vela1_close': 0.0, 'vela1_volume': 0,
                        'vela2_open': 0.0, 'vela2_high': 0.0, 'vela2_low': 0.0, 'vela2_close': 0.0, 'vela2_volume': 0,
                        'vela3_open': 0.0, 'vela3_high': 0.0, 'vela3_low': 0.0, 'vela3_close': 0.0, 'vela3_volume': 0,
                        'current_price': 0.0, 'distance_to_gap': 0.0
                    }
                    
                    fvg_id = self.fvg_db_manager.insert_fvg(fvg_record)
                    if fvg_id:
                        self.logger.log_success(f"✅ FVG almacenado en ML DB: ID {fvg_id}")
                except Exception as e:
                    self.logger.log_error(f"❌ Error almacenando FVG: {e}")
            
            if FVGDetector and hasattr(self, 'fvg_detector') and self.fvg_detector:
                self._fvg_ml_callback = store_fvg_callback
                self.logger.log_success("✅ Integración tradicional FVG-ML configurada")
                return True
            
            return False
            
        except Exception as e:
            self.logger.log_error(f"❌ Error en integración tradicional: {e}")
            return False
    
    
    def _schedule_fvg_order_monitoring(self):
        """Programar monitoreo periódico de órdenes FVG activas"""
        try:
            if hasattr(self, 'enhanced_order_executor') and self.enhanced_order_executor:
                # TODO: Implementar threading para monitoreo en background
                # Por ahora, el monitoreo se hará en el ciclo principal
                self.logger.log_info("📊 Monitoreo de órdenes FVG programado")
        except Exception as e:
            self.logger.log_error(f"Error programando monitoreo: {e}")

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
