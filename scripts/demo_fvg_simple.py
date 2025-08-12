"""
🚀 DEMO SIMPLE FVG CON DATOS REALES
Prueba rápida del detector FVG

Fecha: Agosto 12, 2025
Estado: Testing básico
"""

import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime
from pathlib import Path

# Agregar src al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from analysis.fvg_detector import FVGDetector

def main():
    print("🚀 DEMO SIMPLE FVG CON DATOS REALES")
    print("=" * 50)
    
    try:
        # 1. Cargar datos reales
        data_path = Path(__file__).parent.parent / "data" / "2025-08-12" / "velas_EURUSD_M5_3meses.csv"
        print(f"📂 Cargando datos desde: {data_path}")
        
        # Cargar solo las últimas 500 velas para prueba rápida
        df = pd.read_csv(data_path)
        df = df.tail(500)  # Últimas 500 velas
        
        print(f"✅ Datos cargados: {len(df)} velas")
        print(f"📊 Rango: {df['datetime'].min()} a {df['datetime'].max()}")
        
        # 2. Preparar datos para detector
        candles = []
        for _, row in df.iterrows():
            candle = {
                'time': pd.to_datetime(row['datetime']),
                'open': float(row['open']),
                'high': float(row['high']),
                'low': float(row['low']),
                'close': float(row['close']),
                'volume': int(row['volume']),
                'symbol': 'EURUSD',
                'timeframe': 'M5'
            }
            candles.append(candle)
        
        print(f"🔄 Preparadas {len(candles)} velas para análisis")
        
        # 3. Crear detector
        detector = FVGDetector({
            'min_gap_size': 0.00005,  # 0.5 pips
            'min_body_ratio': 0.65,   # 65%
            'max_gap_size': 0.005,    # 50 pips
            'validation_enabled': True
        })
        
        print("🔍 Detector FVG inicializado")
        
        # 4. Detectar FVGs
        print("🔄 Procesando velas...")
        start_time = datetime.now()
        
        detected_fvgs = detector.detect_all_fvgs(candles)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # 5. Mostrar resultados
        print(f"\n✅ RESULTADOS:")
        print(f"   📈 FVGs detectados: {len(detected_fvgs)}")
        print(f"   ⏱️ Tiempo: {processing_time:.2f}s")
        print(f"   🚀 Velocidad: {len(candles)/processing_time:.0f} velas/seg")
        
        if detected_fvgs:
            # Contar tipos
            bullish = sum(1 for fvg in detected_fvgs if fvg.type == 'BULLISH')
            bearish = sum(1 for fvg in detected_fvgs if fvg.type == 'BEARISH')
            
            print(f"\n📊 TIPOS:")
            print(f"   🟢 Alcistas: {bullish}")
            print(f"   🔴 Bajistas: {bearish}")
            
            # Estadísticas de tamaño
            sizes_pips = [fvg.gap_size * 10000 for fvg in detected_fvgs]
            print(f"\n📏 TAMAÑOS (pips):")
            print(f"   📊 Promedio: {np.mean(sizes_pips):.1f}")
            print(f"   📈 Máximo: {np.max(sizes_pips):.1f}")
            print(f"   📉 Mínimo: {np.min(sizes_pips):.1f}")
            
            # Mostrar últimos 5 FVGs
            print(f"\n🎯 ÚLTIMOS 5 FVGs:")
            recent_fvgs = sorted(detected_fvgs, key=lambda x: x.formation_time, reverse=True)[:5]
            
            for i, fvg in enumerate(recent_fvgs, 1):
                icon = "🟢" if fvg.type == "BULLISH" else "🔴"
                gap_pips = fvg.gap_size * 10000
                time_str = fvg.formation_time.strftime('%m-%d %H:%M')
                print(f"   {i}. {icon} {fvg.type:7s} | {gap_pips:4.1f} pips | {time_str}")
        
        # 6. Métricas del detector
        metrics = detector.get_performance_metrics()
        print(f"\n📈 PERFORMANCE:")
        print(f"   ✅ Precisión: {metrics['accuracy_rate']:.1f}%")
        print(f"   ⚡ Tiempo/detección: {metrics['avg_processing_time_ms']:.2f}ms")
        
        print(f"\n✅ Demo completado exitosamente!")
        
        return detected_fvgs
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

if __name__ == "__main__":
    main()
