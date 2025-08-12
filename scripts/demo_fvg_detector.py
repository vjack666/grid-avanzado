"""
🚀 DEMO FVG DETECTOR INTEGRATION
Integración del detector FVG con el sistema existente

Fecha: Agosto 12, 2025
Oficina: Detección - Piso 3
Estado: Demo de Integración
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
import pandas as pd

# Agregar src al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# Imports del sistema existente
from core.data_manager import DataManager
from analysis.fvg_detector import FVGDetector, RealTimeFVGDetector

class FVGSystemIntegration:
    """
    🔗 INTEGRACIÓN FVG CON SISTEMA EXISTENTE
    
    Conecta el detector FVG con DataManager y otros componentes
    """
    
    def __init__(self):
        self.data_manager = DataManager()
        self.fvg_detector = FVGDetector()
        self.real_time_detector = RealTimeFVGDetector(
            symbols=['EURUSD'],
            timeframes=['M5', 'M15', 'H1']
        )
        
        # Configurar callbacks
        self.real_time_detector.set_callbacks(
            on_fvg_detected=self.on_new_fvg_detected,
            on_fvg_filled=self.on_fvg_filled
        )
        
        print("🔗 FVG System Integration inicializado")
    
    async def on_new_fvg_detected(self, fvg):
        """Callback cuando se detecta nuevo FVG"""
        print(f"🎯 NUEVO FVG DETECTADO:")
        print(f"   Tipo: {fvg.type}")
        print(f"   Símbolo: {fvg.symbol} {fvg.timeframe}")
        print(f"   Tamaño: {fvg.gap_size * 10000:.1f} pips")
        print(f"   Gap: {fvg.gap_low:.5f} - {fvg.gap_high:.5f}")
        print(f"   Tiempo: {fvg.formation_time}")
        print()
    
    async def on_fvg_filled(self, fvg, fill_candle):
        """Callback cuando se llena un FVG"""
        print(f"🎯 FVG LLENADO:")
        print(f"   Tipo: {fvg.type}")
        print(f"   Tamaño: {fvg.gap_size * 10000:.1f} pips")
        print(f"   Precio llenado: {fill_candle['close']:.5f}")
        print()
    
    def demo_historical_detection(self):
        """Demo de detección en datos históricos"""
        print("📊 DEMO: Detección FVG en datos históricos")
        print("=" * 50)
        
        try:
            # Obtener datos históricos
            symbol = 'EURUSD'
            timeframe = 'M5'
            
            print(f"Obteniendo datos para {symbol} {timeframe}...")
            
            # Simular datos si no tenemos DataManager funcionando
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=24)  # Últimas 24 horas
            
            # Generar datos de ejemplo
            candles_data = self._generate_sample_candles(start_time, end_time, symbol, timeframe)
            
            print(f"Procesando {len(candles_data)} velas...")
            
            # Detectar FVGs
            detected_fvgs = self.fvg_detector.detect_all_fvgs(candles_data)
            
            print(f"\n✅ RESULTADOS:")
            print(f"   Total FVGs detectados: {len(detected_fvgs)}")
            
            # Mostrar detalles de cada FVG
            for i, fvg in enumerate(detected_fvgs, 1):
                print(f"\n📈 FVG #{i}:")
                print(f"   Tipo: {fvg.type}")
                print(f"   Tamaño: {fvg.gap_size * 10000:.1f} pips")
                print(f"   Gap: {fvg.gap_low:.5f} - {fvg.gap_high:.5f}")
                print(f"   Formación: {fvg.formation_time}")
            
            # Métricas de performance
            metrics = self.fvg_detector.get_performance_metrics()
            print(f"\n📊 MÉTRICAS DE PERFORMANCE:")
            print(f"   Detecciones totales: {metrics['total_detections']}")
            print(f"   Detecciones válidas: {metrics['valid_detections']}")
            print(f"   Tasa de precisión: {metrics['accuracy_rate']:.1f}%")
            print(f"   Tiempo promedio: {metrics['avg_processing_time_ms']:.2f}ms")
            
        except Exception as e:
            print(f"❌ Error en demo histórico: {str(e)}")
    
    async def demo_real_time_detection(self):
        """Demo de detección en tiempo real"""
        print("\n⚡ DEMO: Detección FVG en tiempo real")
        print("=" * 50)
        
        print("Simulando flujo de velas en tiempo real...")
        print("(Presiona Ctrl+C para detener)\n")
        
        try:
            # Simular flujo de velas en tiempo real
            symbol = 'EURUSD'
            timeframe = 'M5'
            
            # Generar velas base
            base_time = datetime.now()
            base_price = 1.1000
            
            for i in range(20):  # Simular 20 velas
                # Generar vela con movimiento aleatorio
                candle = self._generate_random_candle(
                    base_time + timedelta(minutes=i*5),
                    base_price + (i * 0.0001),  # Tendencia alcista ligera
                    symbol,
                    timeframe
                )
                
                # Procesar vela en tiempo real
                new_fvgs = await self.real_time_detector.process_new_candle(
                    symbol, timeframe, candle
                )
                
                # Mostrar vela procesada
                print(f"⏰ Vela {i+1}: {candle['time'].strftime('%H:%M')} | "
                      f"OHLC: {candle['open']:.5f} {candle['high']:.5f} "
                      f"{candle['low']:.5f} {candle['close']:.5f}")
                
                if new_fvgs:
                    print(f"   🎯 {len(new_fvgs)} FVG(s) detectado(s)")
                
                # Pausa para simular tiempo real
                await asyncio.sleep(0.5)
            
            # Mostrar FVGs activos al final
            active_fvgs = self.real_time_detector.get_active_fvgs()
            print(f"\n📊 RESUMEN FINAL:")
            print(f"   FVGs activos: {len(active_fvgs)}")
            
            for fvg in active_fvgs:
                print(f"   - {fvg.type}: {fvg.gap_size * 10000:.1f} pips")
            
        except KeyboardInterrupt:
            print("\n⏹️ Demo detenido por usuario")
        except Exception as e:
            print(f"❌ Error en demo tiempo real: {str(e)}")
    
    def _generate_sample_candles(self, start_time, end_time, symbol, timeframe):
        """Genera velas de ejemplo para testing"""
        candles = []
        current_time = start_time
        current_price = 1.1000
        
        # Generar velas cada 5 minutos
        while current_time < end_time:
            # Simular movimiento de precio
            price_change = (hash(str(current_time)) % 100 - 50) * 0.00001
            current_price += price_change
            
            # Crear vela con algo de volatilidad
            spread = 0.0002  # 2 pips de spread
            
            open_price = current_price
            close_price = current_price + ((hash(str(current_time + timedelta(minutes=1))) % 100 - 50) * 0.00002)
            high_price = max(open_price, close_price) + (hash(str(current_time + timedelta(minutes=2))) % 10) * 0.00001
            low_price = min(open_price, close_price) - (hash(str(current_time + timedelta(minutes=3))) % 10) * 0.00001
            
            candle = {
                'time': current_time.isoformat(),
                'open': round(open_price, 5),
                'high': round(high_price, 5),
                'low': round(low_price, 5),
                'close': round(close_price, 5),
                'volume': 1000 + (hash(str(current_time)) % 500),
                'symbol': symbol,
                'timeframe': timeframe
            }
            
            candles.append(candle)
            current_price = close_price
            current_time += timedelta(minutes=5)
        
        return candles
    
    def _generate_random_candle(self, timestamp, base_price, symbol, timeframe):
        """Genera una vela aleatoria para simulación"""
        import random
        
        # Generar OHLC con algo de lógica
        open_price = base_price + random.uniform(-0.0005, 0.0005)
        close_price = open_price + random.uniform(-0.0010, 0.0010)
        
        high_price = max(open_price, close_price) + random.uniform(0, 0.0003)
        low_price = min(open_price, close_price) - random.uniform(0, 0.0003)
        
        return {
            'time': timestamp,
            'open': round(open_price, 5),
            'high': round(high_price, 5),
            'low': round(low_price, 5),
            'close': round(close_price, 5),
            'volume': random.randint(800, 1500),
            'symbol': symbol,
            'timeframe': timeframe
        }

async def main():
    """Función principal del demo"""
    print("🚀 DEMO FVG DETECTOR - PISO 3")
    print("=" * 60)
    print()
    
    # Crear integración
    integration = FVGSystemIntegration()
    
    # Demo histórico
    integration.demo_historical_detection()
    
    # Pausa entre demos
    print("\n" + "="*60)
    input("Presiona Enter para continuar al demo en tiempo real...")
    
    # Demo tiempo real
    await integration.demo_real_time_detection()
    
    print("\n✅ Demo completado!")

if __name__ == "__main__":
    asyncio.run(main())
