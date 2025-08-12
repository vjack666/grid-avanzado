"""
🚀 DEMO FVG DETECTOR CON DATOS REALES
Implementación completa usando datos reales del sistema

Fecha: Agosto 12, 2025
Oficina: Detección - Piso 3
Estado: Integración con Datos Reales
"""

import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Agregar src al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from analysis.fvg_detector import FVGDetector, RealTimeFVGDetector
from core.data_manager import DataManager
from core.config_manager import ConfigManager
from core.logger_manager import LoggerManager

class RealDataFVGSystem:
    """
    🔗 SISTEMA FVG CON DATOS REALES
    
    Integra el detector FVG con datos reales del trading grid
    """
    
    def __init__(self):
        """Inicializa el sistema con componentes reales"""
        # Inicializar componentes del sistema existente
        self.config_manager = ConfigManager()
        self.logger_manager = LoggerManager()
        self.data_manager = DataManager(
            config_manager=self.config_manager,
            logger_manager=self.logger_manager
        )
        
        # Inicializar detector FVG
        self.fvg_detector = FVGDetector({
            'min_gap_size': 0.00005,  # 0.5 pips para EURUSD
            'min_body_ratio': 0.65,   # 65% para ser más permisivo con datos reales
            'max_gap_size': 0.005,    # 50 pips máximo
            'validation_enabled': True
        })
        
        # Configurar paths de datos
        self.data_path = Path(__file__).parent.parent / "data"
        self.latest_data_folder = self._get_latest_data_folder()
        
        print("🔗 Sistema FVG con datos reales inicializado")
        print(f"📂 Usando datos de: {self.latest_data_folder}")
    
    def _get_latest_data_folder(self):
        """Obtiene la carpeta de datos más reciente"""
        data_folders = [f for f in self.data_path.iterdir() if f.is_dir() and f.name.startswith("2025")]
        if not data_folders:
            raise ValueError("No se encontraron carpetas de datos")
        
        # Ordenar por fecha y tomar la más reciente
        latest_folder = sorted(data_folders, key=lambda x: x.name, reverse=True)[0]
        return latest_folder
    
    def load_real_data(self, symbol="EURUSD", timeframe="M5", limit=None):
        """
        Carga datos reales desde archivos CSV
        
        Args:
            symbol: Símbolo a cargar
            timeframe: Timeframe (M5, M15, H1, H4)
            limit: Límite de filas (None para todo)
            
        Returns:
            DataFrame con datos reales
        """
        filename = f"velas_{symbol}_{timeframe}_3meses.csv"
        filepath = self.latest_data_folder / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {filepath}")
        
        print(f"📊 Cargando datos reales: {filename}")
        
        # Leer CSV
        df = pd.read_csv(filepath)
        
        # Aplicar límite si se especifica
        if limit:
            df = df.tail(limit)  # Tomar las últimas N filas (más recientes)
        
        # Convertir datetime
        df['datetime'] = pd.to_datetime(df['datetime'])
        
        # Agregar columna time para compatibilidad con detector
        df['time'] = df['datetime']
        
        print(f"✅ Datos cargados: {len(df)} velas desde {df['datetime'].min()} hasta {df['datetime'].max()}")
        
        return df
    
    def detect_fvgs_in_real_data(self, symbol="EURUSD", timeframe="M5", limit=1000):
        """
        Detecta FVGs en datos reales
        
        Args:
            symbol: Símbolo a analizar
            timeframe: Timeframe a analizar
            limit: Número de velas a analizar (más recientes)
        """
        print(f"🔍 DETECCIÓN FVG EN DATOS REALES")
        print(f"Symbol: {symbol} | Timeframe: {timeframe} | Límite: {limit} velas")
        print("=" * 70)
        
        try:
            # Cargar datos reales
            df = self.load_real_data(symbol, timeframe, limit)
            
            # Convertir DataFrame a lista de diccionarios para el detector
            candles = []
            for _, row in df.iterrows():
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
                candles.append(candle)
            
            print(f"🔄 Procesando {len(candles)} velas...")
            
            # Detectar FVGs
            start_time = datetime.now()
            detected_fvgs = self.fvg_detector.detect_all_fvgs(candles)
            processing_time = (datetime.now() - start_time).total_seconds()
            
            print(f"\n✅ RESULTADOS DE DETECCIÓN:")
            print(f"   📈 Total FVGs detectados: {len(detected_fvgs)}")
            print(f"   ⏱️ Tiempo de procesamiento: {processing_time:.3f}s")
            print(f"   🚀 Velocidad: {len(candles)/processing_time:.0f} velas/segundo")
            
            # Analizar tipos de FVG
            bullish_count = sum(1 for fvg in detected_fvgs if fvg.type == 'BULLISH')
            bearish_count = sum(1 for fvg in detected_fvgs if fvg.type == 'BEARISH')
            
            print(f"\n📊 DISTRIBUCIÓN POR TIPO:")
            print(f"   🟢 FVGs Alcistas: {bullish_count} ({bullish_count/max(1,len(detected_fvgs))*100:.1f}%)")
            print(f"   🔴 FVGs Bajistas: {bearish_count} ({bearish_count/max(1,len(detected_fvgs))*100:.1f}%)")
            
            # Analizar tamaños
            if detected_fvgs:
                gap_sizes = [fvg.gap_size * 10000 for fvg in detected_fvgs]  # En pips
                print(f"\n📏 ANÁLISIS DE TAMAÑOS (pips):")
                print(f"   📊 Promedio: {np.mean(gap_sizes):.1f} pips")
                print(f"   📈 Máximo: {np.max(gap_sizes):.1f} pips")
                print(f"   📉 Mínimo: {np.min(gap_sizes):.1f} pips")
                print(f"   📊 Mediana: {np.median(gap_sizes):.1f} pips")
            
            # Mostrar los últimos 10 FVGs detectados
            print(f"\n🎯 ÚLTIMOS {min(10, len(detected_fvgs))} FVGs DETECTADOS:")
            print("-" * 70)
            
            recent_fvgs = sorted(detected_fvgs, key=lambda x: x.formation_time, reverse=True)[:10]
            
            for i, fvg in enumerate(recent_fvgs, 1):
                gap_pips = fvg.gap_size * 10000
                icon = "🟢" if fvg.type == "BULLISH" else "🔴"
                print(f"{i:2d}. {icon} {fvg.type:7s} | {gap_pips:5.1f} pips | "
                      f"{fvg.formation_time.strftime('%Y-%m-%d %H:%M')} | "
                      f"Gap: {fvg.gap_low:.5f}-{fvg.gap_high:.5f}")
            
            # Métricas de performance del detector
            metrics = self.fvg_detector.get_performance_metrics()
            print(f"\n📈 MÉTRICAS DE PERFORMANCE:")
            print(f"   ✅ Precisión: {metrics['accuracy_rate']:.1f}%")
            print(f"   ⚡ Tiempo promedio: {metrics['avg_processing_time_ms']:.2f}ms por detección")
            print(f"   🎯 Detecciones válidas: {metrics['valid_detections']}")
            print(f"   ❌ Falsos positivos: {metrics['false_positives']}")
            
            return detected_fvgs
            
        except Exception as e:
            print(f"❌ Error en detección: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    def analyze_fvg_patterns_by_session(self, symbol="EURUSD", timeframe="M5", limit=5000):
        """
        Analiza patrones de FVG por sesión de trading
        """
        print(f"\n📊 ANÁLISIS DE FVG POR SESIONES")
        print("=" * 50)
        
        try:
            # Cargar más datos para análisis estadístico
            df = self.load_real_data(symbol, timeframe, limit)
            
            # Convertir a candles
            candles = []
            for _, row in df.iterrows():
                candle = {
                    'time': row['datetime'],
                    'open': float(row['open']),
                    'high': float(row['high']),
                    'low': float(row['low']),
                    'close': float(row['close']),
                    'volume': int(row['volume']),
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'hour': row['hour'],
                    'weekday': row['weekday']
                }
                candles.append(candle)
            
            # Detectar FVGs
            detected_fvgs = self.fvg_detector.detect_all_fvgs(candles)
            
            if not detected_fvgs:
                print("❌ No se detectaron FVGs para análisis")
                return
            
            # Clasificar por sesiones
            session_stats = {
                'ASIA': {'count': 0, 'total_pips': 0},      # 21:00-06:00 UTC
                'LONDON': {'count': 0, 'total_pips': 0},    # 07:00-16:00 UTC
                'NY': {'count': 0, 'total_pips': 0},        # 13:00-22:00 UTC
                'OVERLAP': {'count': 0, 'total_pips': 0}    # 13:00-16:00 UTC
            }
            
            for fvg in detected_fvgs:
                hour = fvg.formation_time.hour
                gap_pips = fvg.gap_size * 10000
                
                # Clasificar por sesión
                if 21 <= hour or hour <= 6:
                    session = 'ASIA'
                elif 7 <= hour <= 16:
                    session = 'LONDON'
                    if 13 <= hour <= 16:
                        session_stats['OVERLAP']['count'] += 1
                        session_stats['OVERLAP']['total_pips'] += gap_pips
                elif 13 <= hour <= 22:
                    session = 'NY'
                else:
                    continue
                
                session_stats[session]['count'] += 1
                session_stats[session]['total_pips'] += gap_pips
            
            # Mostrar estadísticas por sesión
            total_fvgs = len(detected_fvgs)
            print(f"Total FVGs analizados: {total_fvgs}")
            print()
            
            for session_name, stats in session_stats.items():
                count = stats['count']
                total_pips = stats['total_pips']
                percentage = (count / total_fvgs * 100) if total_fvgs > 0 else 0
                avg_pips = (total_pips / count) if count > 0 else 0
                
                print(f"📊 {session_name:7s}: {count:3d} FVGs ({percentage:5.1f}%) | "
                      f"Promedio: {avg_pips:5.1f} pips | Total: {total_pips:6.1f} pips")
            
        except Exception as e:
            print(f"❌ Error en análisis por sesiones: {str(e)}")
    
    def analyze_fvg_fill_simulation(self, symbol="EURUSD", timeframe="M5", limit=2000):
        """
        Simula el llenado de FVGs usando datos históricos posteriores
        """
        print(f"\n🎯 SIMULACIÓN DE LLENADO DE FVG")
        print("=" * 50)
        
        try:
            # Cargar datos
            df = self.load_real_data(symbol, timeframe, limit)
            
            # Usar solo primeras 80% para detección, 20% restante para simulación de llenado
            split_index = int(len(df) * 0.8)
            detection_df = df.iloc[:split_index]
            future_df = df.iloc[split_index:]
            
            print(f"📊 Datos para detección: {len(detection_df)} velas")
            print(f"📊 Datos para simulación: {len(future_df)} velas")
            
            # Convertir datos de detección
            candles = []
            for _, row in detection_df.iterrows():
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
                candles.append(candle)
            
            # Detectar FVGs en datos históricos
            detected_fvgs = self.fvg_detector.detect_all_fvgs(candles)
            
            if not detected_fvgs:
                print("❌ No se detectaron FVGs para simulación")
                return
            
            print(f"🔍 FVGs detectados para simulación: {len(detected_fvgs)}")
            
            # Simular llenado con datos futuros
            filled_count = 0
            fill_times = []
            
            for fvg in detected_fvgs:
                # Buscar si el FVG se llena en datos futuros
                for _, future_row in future_df.iterrows():
                    future_time = future_row['datetime']
                    
                    # Solo considerar datos posteriores a la formación del FVG
                    if future_time <= fvg.formation_time:
                        continue
                    
                    # Verificar si se llena el FVG
                    is_filled = False
                    if fvg.type == 'BULLISH':
                        # FVG alcista se llena si price toca gap_low
                        if future_row['low'] <= fvg.gap_low:
                            is_filled = True
                    else:
                        # FVG bajista se llena si price toca gap_high
                        if future_row['high'] >= fvg.gap_high:
                            is_filled = True
                    
                    if is_filled:
                        filled_count += 1
                        time_to_fill = future_time - fvg.formation_time
                        fill_times.append(time_to_fill.total_seconds() / 3600)  # En horas
                        break
            
            # Estadísticas de llenado
            fill_rate = (filled_count / len(detected_fvgs) * 100) if detected_fvgs else 0
            
            print(f"\n📈 RESULTADOS DE SIMULACIÓN:")
            print(f"   🎯 FVGs llenados: {filled_count}/{len(detected_fvgs)} ({fill_rate:.1f}%)")
            
            if fill_times:
                print(f"   ⏱️ Tiempo promedio llenado: {np.mean(fill_times):.1f} horas")
                print(f"   ⚡ Llenado más rápido: {np.min(fill_times):.1f} horas")
                print(f"   🐌 Llenado más lento: {np.max(fill_times):.1f} horas")
                print(f"   📊 Mediana tiempo llenado: {np.median(fill_times):.1f} horas")
            
            return {
                'total_fvgs': len(detected_fvgs),
                'filled_count': filled_count,
                'fill_rate': fill_rate,
                'avg_fill_time_hours': np.mean(fill_times) if fill_times else 0
            }
            
        except Exception as e:
            print(f"❌ Error en simulación de llenado: {str(e)}")
            return None

def main():
    """Función principal de demostración"""
    print("🚀 SISTEMA FVG CON DATOS REALES - PISO 3")
    print("=" * 60)
    
    try:
        # Crear sistema
        fvg_system = RealDataFVGSystem()
        
        # 1. Análisis básico con datos recientes
        print("\n" + "="*60)
        print("1️⃣ ANÁLISIS BÁSICO - ÚLTIMAS 1000 VELAS")
        detected_fvgs = fvg_system.detect_fvgs_in_real_data(
            symbol="EURUSD", 
            timeframe="M5", 
            limit=1000
        )
        
        # 2. Análisis por sesiones
        if detected_fvgs:
            print("\n" + "="*60)
            print("2️⃣ ANÁLISIS POR SESIONES DE TRADING")
            fvg_system.analyze_fvg_patterns_by_session(
                symbol="EURUSD", 
                timeframe="M5", 
                limit=3000
            )
        
        # 3. Simulación de llenado
        print("\n" + "="*60)
        print("3️⃣ SIMULACIÓN DE LLENADO HISTÓRICO")
        fill_results = fvg_system.analyze_fvg_fill_simulation(
            symbol="EURUSD", 
            timeframe="M5", 
            limit=5000
        )
        
        # 4. Análisis en H1 para comparación
        print("\n" + "="*60)
        print("4️⃣ ANÁLISIS COMPARATIVO EN H1")
        h1_fvgs = fvg_system.detect_fvgs_in_real_data(
            symbol="EURUSD", 
            timeframe="H1", 
            limit=500
        )
        
        print(f"\n📊 COMPARACIÓN M5 vs H1:")
        print(f"   M5 (1000 velas): {len(detected_fvgs)} FVGs")
        print(f"   H1 (500 velas):  {len(h1_fvgs)} FVGs")
        print(f"   Densidad M5: {len(detected_fvgs)/1000*100:.2f} FVGs/100 velas")
        print(f"   Densidad H1: {len(h1_fvgs)/500*100:.2f} FVGs/100 velas")
        
        print("\n✅ DEMOSTRACIÓN COMPLETADA CON DATOS REALES!")
        print("\n🎯 PRÓXIMOS PASOS:")
        print("   1. Implementar Oficina de Análisis para evaluación de calidad")
        print("   2. Agregar Oficina de IA para predicciones ML")
        print("   3. Desarrollar Oficina de Trading para señales automáticas")
        print("   4. Crear Centro de Control para monitoreo en tiempo real")
        
    except Exception as e:
        print(f"❌ Error en demostración: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
