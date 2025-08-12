"""
🚀 DEMO EXPANSIÓN MULTI-TIMEFRAME CON DATOS REALES
Sistema completo de detección expandida con alertas

Fecha: Agosto 12, 2025
Oficina: Detección Expandida - Piso 3
Estado: Demo Integración Completa
"""

import pandas as pd
import numpy as np
import asyncio
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

# Agregar src al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from analysis.fvg_detector import FVGDetector
from analysis.multi_timeframe_detector import MultiTimeframeFVGDetector
from analysis.fvg_alert_system import FVGAlertSystem, AlertType, AlertPriority

class ExpandedFVGSystem:
    """
    🔍 SISTEMA FVG EXPANDIDO COMPLETO
    
    Integra:
    - Detección multi-timeframe
    - Análisis de confluencias
    - Sistema de alertas
    - Métricas por sesión
    - Datos reales
    """
    
    def __init__(self):
        """Inicializa el sistema expandido"""
        # Componentes principales
        self.multi_detector = MultiTimeframeFVGDetector("EURUSD")
        self.alert_system = FVGAlertSystem({
            'max_alerts_per_minute': 20,
            'min_priority': AlertPriority.LOW,
            'throttling_enabled': False  # Desactivar para demo
        })
        
        # Paths de datos
        self.data_path = Path(__file__).parent.parent / "data"
        self.latest_data_folder = self._get_latest_data_folder()
        
        print("🚀 Sistema FVG Expandido inicializado")
        print(f"📂 Datos: {self.latest_data_folder}")
    
    def _get_latest_data_folder(self):
        """Obtiene la carpeta de datos más reciente"""
        data_folders = [f for f in self.data_path.iterdir() if f.is_dir() and f.name.startswith("2025")]
        return sorted(data_folders, key=lambda x: x.name, reverse=True)[0]
    
    def load_multi_timeframe_data(self, symbol="EURUSD", limit_per_tf=None):
        """
        Carga datos reales para múltiples timeframes
        
        Args:
            symbol: Símbolo a cargar
            limit_per_tf: Límite de velas por timeframe
            
        Returns:
            Dict con DataFrames por timeframe
        """
        timeframes = ['M5', 'M15', 'H1', 'H4']
        data_by_tf = {}
        
        print(f"📊 Cargando datos multi-timeframe para {symbol}")
        
        for tf in timeframes:
            filename = f"velas_{symbol}_{tf}_3meses.csv"
            filepath = self.latest_data_folder / filename
            
            if not filepath.exists():
                print(f"⚠️ Archivo no encontrado: {filename}")
                continue
            
            try:
                df = pd.read_csv(filepath)
                
                if limit_per_tf:
                    df = df.tail(limit_per_tf)
                
                df['datetime'] = pd.to_datetime(df['datetime'])
                data_by_tf[tf] = df
                
                print(f"   ✅ {tf}: {len(df)} velas | "
                      f"{df['datetime'].min().strftime('%m-%d %H:%M')} a "
                      f"{df['datetime'].max().strftime('%m-%d %H:%M')}")
                
            except Exception as e:
                print(f"   ❌ Error cargando {tf}: {e}")
        
        return data_by_tf
    
    async def run_complete_analysis(self, symbol="EURUSD", limit=500):
        """
        Ejecuta análisis completo multi-timeframe con alertas
        
        Args:
            symbol: Símbolo a analizar
            limit: Límite de velas por timeframe
        """
        print(f"\n🔍 ANÁLISIS COMPLETO MULTI-TIMEFRAME: {symbol}")
        print("=" * 70)
        
        try:
            # 1. Cargar datos multi-timeframe
            data_by_tf = self.load_multi_timeframe_data(symbol, limit)
            
            if not data_by_tf:
                print("❌ No se pudieron cargar datos")
                return
            
            # 2. Ejecutar análisis multi-timeframe
            print(f"\n🔄 Procesando análisis multi-timeframe...")
            analysis = self.multi_detector.analyze_multi_timeframe_data(data_by_tf)
            
            # 3. Generar alertas basadas en análisis
            print(f"\n🚨 Generando alertas...")
            alerts = self.multi_detector.generate_alerts(analysis)
            
            # 4. Enviar alertas específicas
            await self._process_alerts(alerts, symbol)
            
            # 5. Análisis adicional de patrones
            await self._analyze_advanced_patterns(analysis, symbol)
            
            # 6. Mostrar estadísticas finales
            self._show_final_statistics(analysis)
            
            return analysis
            
        except Exception as e:
            print(f"❌ Error en análisis completo: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def _process_alerts(self, alerts: List[Dict], symbol: str):
        """Procesa y envía alertas generadas"""
        if not alerts:
            print("   ℹ️ No se generaron alertas")
            return
        
        print(f"   📨 Procesando {len(alerts)} alertas...")
        
        for alert in alerts:
            alert_type_map = {
                'CONFLUENCE': AlertType.CONFLUENCE,
                'LARGE_FVG': AlertType.LARGE_FVG,
                'MARKET_BIAS': AlertType.MARKET_BIAS,
                'SESSION_CONCENTRATION': AlertType.SESSION_CONCENTRATION
            }
            
            alert_type = alert_type_map.get(alert['type'], AlertType.NEW_FVG)
            priority_map = {
                'LOW': AlertPriority.LOW,
                'MEDIUM': AlertPriority.MEDIUM,
                'HIGH': AlertPriority.HIGH,
                'CRITICAL': AlertPriority.CRITICAL
            }
            priority = priority_map.get(alert['priority'], AlertPriority.MEDIUM)
            
            await self.alert_system.send_alert(
                alert_type=alert_type,
                title=alert['message'],
                message=f"Detalles: {alert.get('data', {})}",
                symbol=symbol,
                priority=priority,
                timeframe=alert.get('timeframe'),
                data=alert.get('data', {})
            )
    
    async def _analyze_advanced_patterns(self, analysis, symbol: str):
        """Análisis avanzado de patrones"""
        print(f"\n📈 ANÁLISIS AVANZADO DE PATRONES")
        print("-" * 50)
        
        # Análisis de densidad FVG por timeframe
        print("📊 Densidad FVG por Timeframe:")
        for tf, fvgs in analysis.timeframe_data.items():
            density = len(fvgs) / 100  # FVGs por 100 velas
            print(f"   {tf:3s}: {density:.2f} FVGs/100 velas")
        
        # Análisis de correlación entre timeframes
        print(f"\n🔗 Análisis de Correlaciones:")
        self._analyze_timeframe_correlations(analysis.timeframe_data)
        
        # Análisis de timing de confluencias
        if analysis.confluence_fvgs:
            print(f"\n⏰ Análisis de Confluencias:")
            strong_confluences = [c for c in analysis.confluence_fvgs if c['confluence_strength'] >= 7.0]
            print(f"   Confluencias fuertes: {len(strong_confluences)}/{len(analysis.confluence_fvgs)}")
            
            # Alertas para confluencias fuertes
            for conf in strong_confluences:
                await self.alert_system.send_confluence_alert(conf, symbol)
    
    def _analyze_timeframe_correlations(self, timeframe_data):
        """Analiza correlaciones entre timeframes"""
        timeframes = list(timeframe_data.keys())
        
        for i, tf1 in enumerate(timeframes):
            for tf2 in timeframes[i+1:]:
                fvgs1 = timeframe_data[tf1]
                fvgs2 = timeframe_data[tf2]
                
                # Análisis simple de correlación por tipo
                bullish1 = sum(1 for fvg in fvgs1 if fvg.type == 'BULLISH')
                bullish2 = sum(1 for fvg in fvgs2 if fvg.type == 'BULLISH')
                
                total1, total2 = len(fvgs1), len(fvgs2)
                
                if total1 > 0 and total2 > 0:
                    ratio1 = bullish1 / total1
                    ratio2 = bullish2 / total2
                    correlation = 1 - abs(ratio1 - ratio2)  # Correlación simple
                    
                    print(f"   {tf1}-{tf2}: {correlation:.2f} correlación")
    
    def _show_final_statistics(self, analysis):
        """Muestra estadísticas finales del análisis"""
        print(f"\n📊 ESTADÍSTICAS FINALES")
        print("=" * 50)
        
        # Métricas del detector multi-timeframe
        metrics = self.multi_detector.get_global_metrics()
        print(f"🎯 Total detecciones: {metrics.get('total_detections', 0)}")
        print(f"🔗 Confluencias: {metrics.get('confluence_detections', 0)}")
        
        # Distribución por sesión
        session_dist = metrics.get('session_distribution', {})
        if session_dist:
            print(f"\n🕒 Distribución por Sesión:")
            for session, count in session_dist.items():
                percentage = (count / sum(session_dist.values()) * 100) if session_dist.values() else 0
                print(f"   {session:8s}: {count:3d} ({percentage:5.1f}%)")
        
        # Métricas del sistema de alertas
        alert_metrics = self.alert_system.get_metrics()
        print(f"\n🚨 Métricas de Alertas:")
        print(f"   📨 Alertas enviadas: {alert_metrics['sent_alerts']}")
        print(f"   🔇 Alertas suprimidas: {alert_metrics['suppressed_alerts']}")
        print(f"   ❌ Fallos de envío: {alert_metrics['failed_sends']}")
    
    async def demo_real_time_simulation(self, symbol="EURUSD", timeframe="M5", duration_minutes=10):
        """
        Simula procesamiento en tiempo real
        
        Args:
            symbol: Símbolo a simular
            timeframe: Timeframe base
            duration_minutes: Duración de la simulación
        """
        print(f"\n⚡ SIMULACIÓN TIEMPO REAL")
        print(f"Símbolo: {symbol} | TF: {timeframe} | Duración: {duration_minutes}min")
        print("=" * 60)
        
        # Cargar datos para simulación
        data = self.load_multi_timeframe_data(symbol, limit_per_tf=1000)
        
        if timeframe not in data:
            print(f"❌ No hay datos para {timeframe}")
            return
        
        df = data[timeframe]
        simulation_candles = df.tail(duration_minutes * 12).copy()  # 12 velas de M5 por hora
        
        print(f"🔄 Simulando {len(simulation_candles)} velas...")
        print("(Presiona Ctrl+C para detener)\n")
        
        detector = FVGDetector()
        candle_buffer = []
        
        try:
            for i, (_, row) in enumerate(simulation_candles.iterrows()):
                # Preparar vela actual
                candle = {
                    'time': row['datetime'],
                    'open': float(row['open']),
                    'high': float(row['high']),
                    'low': float(row['low']),
                    'close': float(row['close']),
                    'volume': int(row['volume']),
                    'symbol': symbol,
                    'timeframe': timeframe
                }
                
                candle_buffer.append(candle)
                
                # Mostrar vela actual
                time_str = candle['time'].strftime('%H:%M')
                print(f"⏰ {i+1:3d}. {time_str} | "
                      f"OHLC: {candle['open']:.5f} {candle['high']:.5f} "
                      f"{candle['low']:.5f} {candle['close']:.5f}")
                
                # Detectar FVGs si tenemos suficientes velas
                if len(candle_buffer) >= 3:
                    # Detectar FVG bullish
                    bullish_fvg = detector.detect_bullish_fvg(candle_buffer[-3:])
                    if bullish_fvg:
                        gap_pips = bullish_fvg.gap_size * 10000
                        print(f"     🟢 FVG BULLISH: {gap_pips:.1f} pips")
                        await self.alert_system.send_fvg_alert(
                            bullish_fvg.to_dict(), symbol, timeframe
                        )
                    
                    # Detectar FVG bearish
                    bearish_fvg = detector.detect_bearish_fvg(candle_buffer[-3:])
                    if bearish_fvg:
                        gap_pips = bearish_fvg.gap_size * 10000
                        print(f"     🔴 FVG BEARISH: {gap_pips:.1f} pips")
                        await self.alert_system.send_fvg_alert(
                            bearish_fvg.to_dict(), symbol, timeframe
                        )
                
                # Pausa para simular tiempo real
                await asyncio.sleep(0.5)
        
        except KeyboardInterrupt:
            print("\n⏹️ Simulación detenida por usuario")
        
        # Mostrar resumen de simulación
        print(f"\n📊 RESUMEN SIMULACIÓN:")
        alert_metrics = self.alert_system.get_metrics()
        print(f"   📨 Alertas generadas: {alert_metrics['total_alerts']}")
        print(f"   ⚡ Velas procesadas: {len(candle_buffer)}")

async def main():
    """Función principal de demostración"""
    print("🚀 DEMO EXPANSIÓN MULTI-TIMEFRAME - PISO 3")
    print("=" * 70)
    print()
    
    # Crear sistema expandido
    system = ExpandedFVGSystem()
    
    try:
        # 1. Análisis completo multi-timeframe
        print("1️⃣ EJECUTANDO ANÁLISIS MULTI-TIMEFRAME")
        analysis = await system.run_complete_analysis("EURUSD", limit=300)
        
        if analysis:
            # 2. Pausa entre demos
            print("\n" + "="*70)
            input("Presiona Enter para continuar a la simulación en tiempo real...")
            
            # 3. Simulación tiempo real
            print("\n2️⃣ SIMULACIÓN TIEMPO REAL")
            await system.demo_real_time_simulation("EURUSD", "M5", duration_minutes=5)
            
            # 4. Mostrar historial de alertas
            print("\n3️⃣ HISTORIAL DE ALERTAS")
            print("=" * 40)
            
            alert_history = system.alert_system.get_alert_history(10)
            for i, alert in enumerate(alert_history[:10], 1):
                time_str = pd.to_datetime(alert['timestamp']).strftime('%H:%M:%S')
                print(f"{i:2d}. [{alert['priority']}] {time_str} - {alert['title']}")
        
        print("\n✅ DEMOSTRACIÓN COMPLETA FINALIZADA!")
        
        print("\n🎯 CAPACIDADES IMPLEMENTADAS:")
        print("   ✅ Detección multi-timeframe (M5, M15, H1, H4)")
        print("   ✅ Análisis de confluencias entre timeframes")
        print("   ✅ Sistema de alertas inteligente")
        print("   ✅ Estadísticas por sesión de trading")
        print("   ✅ Simulación tiempo real")
        print("   ✅ Métricas y monitoreo completo")
        
        print("\n🚀 PRÓXIMOS PASOS SUGERIDOS:")
        print("   1. Implementar Oficina de Análisis (calidad FVG)")
        print("   2. Desarrollar Oficina de IA (predicciones ML)")
        print("   3. Crear Oficina de Trading (señales automáticas)")
        print("   4. Integrar con sistema de trading en vivo")
        
    except Exception as e:
        print(f"❌ Error en demostración: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
