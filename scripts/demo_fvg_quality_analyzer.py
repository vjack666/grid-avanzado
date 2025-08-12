"""
🎯 DEMO: FVG QUALITY ANALYZER - PISO 3
======================================

Prueba completa del FVGQualityAnalyzer con datos reales
Evalúa la calidad de FVGs detectados usando múltiples criterios
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from datetime import datetime, timedelta
from src.analysis.piso_3.deteccion.fvg_detector import FVGDetector
from src.analysis.piso_3.analisis import FVGQualityAnalyzer

def main():
    """Demo completo del analizador de calidad de FVGs"""
    print("=" * 60)
    print("🎯 DEMO: FVG QUALITY ANALYZER - PISO 3")
    print("=" * 60)
    
    # 1. Cargar datos reales
    print("\n📊 CARGANDO DATOS REALES...")
    
    # Usar mismo archivo que validamos anteriormente
    filename = "data/2025-08-12/velas_EURUSD_M15_3meses.csv"
    
    if not os.path.exists(filename):
        print(f"❌ Archivo no encontrado: {filename}")
        return
    
    try:
        df = pd.read_csv(filename)
        # Convertir timestamp
        if 'datetime' in df.columns:
            df['timestamp'] = pd.to_datetime(df['datetime'])
        elif 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        print(f"✅ Datos cargados: {len(df)} velas de EURUSD M15")
        
    except Exception as e:
        print(f"❌ Error cargando datos: {e}")
        return
    
    # 2. Detectar FVGs
    print("\n🔍 DETECTANDO FVGS...")
    detector = FVGDetector()
    
    # Convertir DataFrame a formato requerido
    candles = []
    for _, row in df.iterrows():
        candle = {
            'time': row['timestamp'],  # Usar 'time' como requiere el detector
            'timestamp': row['timestamp'],
            'open': float(row['open']),
            'high': float(row['high']),
            'low': float(row['low']),
            'close': float(row['close']),
            'volume': int(row.get('volume', 0)),
            'symbol': 'EURUSD',
            'timeframe': 'M15'
        }
        candles.append(candle)
    
    # Detectar FVGs
    fvgs = detector.detect_all_fvgs(candles)
    print(f"✅ {len(fvgs)} FVGs detectados")
    
    if not fvgs:
        print("❌ No se detectaron FVGs para analizar")
        return
    
    # 3. Inicializar analizador de calidad
    print("\n🎯 INICIALIZANDO QUALITY ANALYZER...")
    quality_analyzer = FVGQualityAnalyzer()
    
    # 4. Analizar calidad de FVGs
    print("\n📊 ANALIZANDO CALIDAD DE FVGS...")
    
    quality_results = []
    market_context = {
        'trend_alignment': 0.7,  # Ejemplo: tendencia alcista moderada
        'sr_proximity': 0.6,     # Ejemplo: cerca de soporte/resistencia
        'momentum': 0.8,         # Ejemplo: momentum fuerte
        'current_price': candles[-1]['close']  # Precio actual
    }
    
    # Calcular volumen promedio para contexto
    avg_volume = sum(c['volume'] for c in candles[-50:]) / 50 if len(candles) >= 50 else 1000
    volume_data = {'avg_volume': avg_volume}
    
    # Analizar cada FVG (limitar a 20 para el demo)
    fvgs_to_analyze = fvgs[:20] if len(fvgs) > 20 else fvgs
    
    for i, fvg in enumerate(fvgs_to_analyze):
        print(f"\n🔄 Analizando FVG {i+1}/{len(fvgs_to_analyze)}...")
        
        # Mejorar FVG con datos adicionales para análisis
        fvg = enhance_fvg_for_analysis(fvg, candles)
        
        # Analizar calidad
        quality_result = quality_analyzer.analyze_fvg_quality(
            fvg, 
            market_context, 
            volume_data
        )
        
        quality_result['fvg'] = fvg
        quality_results.append(quality_result)
        
        print(f"   📊 Score: {quality_result['final_score']:.2f}/10")
        print(f"   🏆 Nivel: {quality_result['quality_level']}")
        print(f"   📏 Tamaño: {fvg.gap_size_pips:.2f} pips")
        print(f"   📈 Tipo: {fvg.type}")
    
    # 5. Generar reporte de calidad
    print("\n" + "=" * 60)
    print("📊 REPORTE DE CALIDAD FVG")
    print("=" * 60)
    
    # Estadísticas generales
    scores = [r['final_score'] for r in quality_results]
    avg_quality = sum(scores) / len(scores)
    max_quality = max(scores)
    min_quality = min(scores)
    
    print(f"\n📈 ESTADÍSTICAS GENERALES:")
    print(f"   📊 FVGs analizados: {len(quality_results)}")
    print(f"   📊 Calidad promedio: {avg_quality:.2f}/10")
    print(f"   📊 Calidad máxima: {max_quality:.2f}/10")
    print(f"   📊 Calidad mínima: {min_quality:.2f}/10")
    
    # Distribución por niveles
    quality_levels = {}
    for result in quality_results:
        level = result['quality_level']
        quality_levels[level] = quality_levels.get(level, 0) + 1
    
    print(f"\n🏆 DISTRIBUCIÓN POR NIVELES:")
    for level, count in sorted(quality_levels.items()):
        percentage = (count / len(quality_results)) * 100
        print(f"   {level}: {count} FVGs ({percentage:.1f}%)")
    
    # Top 5 FVGs de mejor calidad
    print(f"\n🥇 TOP 5 FVGS DE MEJOR CALIDAD:")
    top_fvgs = sorted(quality_results, key=lambda x: x['final_score'], reverse=True)[:5]
    
    for i, result in enumerate(top_fvgs):
        fvg = result['fvg']
        print(f"\n   {i+1}. 🎯 Score: {result['final_score']:.2f}/10")
        print(f"      📊 Nivel: {result['quality_level']}")
        print(f"      📈 Tipo: {fvg.type}")
        print(f"      📏 Tamaño: {fvg.gap_size_pips:.2f} pips")
        print(f"      📊 Scores detallados:")
        for metric, score in result['scores'].items():
            print(f"         {metric}: {score:.2f}/10")
    
    # Análisis de correlaciones
    print(f"\n🔍 ANÁLISIS DE CORRELACIONES:")
    
    # Correlación tamaño vs calidad
    sizes = [r['fvg'].gap_size_pips for r in quality_results]
    size_quality_corr = calculate_correlation(sizes, scores)
    print(f"   📏 Tamaño vs Calidad: {size_quality_corr:.3f}")
    
    # FVGs por tipo
    bullish_scores = [r['final_score'] for r in quality_results if r['fvg'].type == 'BULLISH']
    bearish_scores = [r['final_score'] for r in quality_results if r['fvg'].type == 'BEARISH']
    
    if bullish_scores:
        print(f"   🟢 Calidad promedio BULLISH: {sum(bullish_scores)/len(bullish_scores):.2f}/10")
    if bearish_scores:
        print(f"   🔴 Calidad promedio BEARISH: {sum(bearish_scores)/len(bearish_scores):.2f}/10")
    
    # 6. Sugerencias de mejora
    print(f"\n💡 SUGERENCIAS DE MEJORA:")
    
    low_quality_count = len([r for r in quality_results if r['final_score'] < 5.0])
    if low_quality_count > 0:
        print(f"   ⚠️ {low_quality_count} FVGs con calidad baja (<5.0)")
        print(f"   💡 Considerar filtrar FVGs con calidad < 6.0")
    
    excellent_count = len([r for r in quality_results if r['final_score'] >= 8.5])
    if excellent_count > 0:
        print(f"   ✅ {excellent_count} FVGs de calidad excelente (≥8.5)")
        print(f"   🎯 Enfocar trading en FVGs de alta calidad")
    
    print(f"\n✅ Demo del FVGQualityAnalyzer completado!")

def enhance_fvg_for_analysis(fvg, candles):
    """
    Mejora el FVG con datos adicionales para análisis de calidad
    """
    # Encontrar las velas de formación
    fvg_timestamp = fvg.formation_time
    fvg_index = None
    
    # Buscar el índice de la vela del FVG
    for i, candle in enumerate(candles):
        if candle['timestamp'] == fvg_timestamp:
            fvg_index = i
            break
    
    if fvg_index and fvg_index >= 2:
        # Obtener velas de formación (anterior, actual, siguiente)
        formation_candles = [
            candles[fvg_index - 1],  # Vela anterior
            candles[fvg_index],      # Vela del FVG
            candles[fvg_index + 1] if fvg_index + 1 < len(candles) else candles[fvg_index]
        ]
        fvg.formation_candles = formation_candles
    
    # Calcular tamaño en pips (si no existe)
    if not hasattr(fvg, 'gap_size_pips'):
        if hasattr(fvg, 'gap_size'):
            fvg.gap_size_pips = fvg.gap_size * 10000  # Convertir a pips para EURUSD
        else:
            fvg.gap_size_pips = abs(fvg.gap_high - fvg.gap_low) * 10000
    
    return fvg

def calculate_correlation(x, y):
    """Calcula correlación simple entre dos listas"""
    if len(x) != len(y) or len(x) < 2:
        return 0.0
    
    n = len(x)
    sum_x = sum(x)
    sum_y = sum(y)
    sum_xy = sum(x[i] * y[i] for i in range(n))
    sum_x2 = sum(xi ** 2 for xi in x)
    sum_y2 = sum(yi ** 2 for yi in y)
    
    numerator = n * sum_xy - sum_x * sum_y
    denominator = ((n * sum_x2 - sum_x ** 2) * (n * sum_y2 - sum_y ** 2)) ** 0.5
    
    return numerator / denominator if denominator != 0 else 0.0

if __name__ == "__main__":
    main()
