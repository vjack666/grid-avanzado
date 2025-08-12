"""
🔗 DEMO: CONFLUENCE ANALYZER - PISO 3
====================================

Prueba completa del ConfluenceAnalyzer con datos reales
Detecta confluencias entre FVGs de múltiples timeframes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from datetime import datetime, timedelta
from src.core.data_manager import DataManager
from src.analysis.fvg_detector import FVGDetector
from src.analysis.multi_timeframe_detector import MultiTimeframeFVGDetector
from src.analysis.piso_3.deteccion import ConfluenceAnalyzer

def main():
    """Demo completo del analizador de confluencias"""
    print("=" * 60)
    print("🔗 DEMO: CONFLUENCE ANALYZER - PISO 3")
    print("=" * 60)
    
    # 1. Cargar datos reales
    print("\n📊 CARGANDO DATOS REALES...")
    data_manager = DataManager()
    
    # Obtener datos de múltiples timeframes
    timeframes = ["M5", "M15", "H1", "H4"]
    all_data = {}
    
    for tf in timeframes:
        try:
            filename = f"data/2025-08-12/velas_EURUSD_{tf}_3meses.csv"
            if os.path.exists(filename):
                df = pd.read_csv(filename)
                # Los archivos usan 'datetime' no 'timestamp'
                if 'datetime' in df.columns:
                    df['timestamp'] = pd.to_datetime(df['datetime'])
                elif 'timestamp' in df.columns:
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                all_data[tf] = df
                print(f"✅ {tf}: {len(df)} velas cargadas")
            else:
                print(f"❌ {tf}: Archivo no encontrado")
        except Exception as e:
            print(f"❌ Error cargando {tf}: {e}")
    
    if not all_data:
        print("❌ No se pudieron cargar datos")
        return
    
    # 2. Detectar FVGs en múltiples timeframes
    print("\n🔍 DETECTANDO FVGS EN MÚLTIPLES TIMEFRAMES...")
    
    # Usar FVGDetector individual para cada timeframe
    detector = FVGDetector()
    all_fvgs = {}
    
    for tf, df in all_data.items():
        print(f"\n🔄 Procesando {tf}...")
        
        # Convertir DataFrame a formato requerido
        candles = []
        for _, row in df.iterrows():
            candle = {
                'timestamp': row['timestamp'],
                'open': float(row['open']),
                'high': float(row['high']),
                'low': float(row['low']),
                'close': float(row['close']),
                'volume': int(row.get('volume', 0))
            }
            candles.append(candle)
        
        # Detectar FVGs
        fvgs = detector.detect_all_fvgs(candles)
        all_fvgs[tf] = fvgs
        
        print(f"   📊 {len(fvgs)} FVGs detectados en {tf}")
        
        # Mostrar algunos ejemplos
        if fvgs:
            for i, fvg in enumerate(fvgs[:3]):
                print(f"   • FVG {i+1}: {fvg.type} - Size: {fvg.gap_size:.5f}")
    
    # También probar el MultiTimeframeDetector con todos los datos
    print(f"\n🔍 ANÁLISIS MULTI-TIMEFRAME COMPLETO...")
    mtf_detector = MultiTimeframeFVGDetector()
    mtf_analysis = mtf_detector.analyze_multi_timeframe_data(all_data)
    
    print(f"✅ Análisis multi-timeframe completado")
    print(f"📊 Total timeframes analizados: {len(mtf_analysis.timeframe_data)}")
    
    # Usar FVGs del análisis individual para confluencias
    fvgs_for_confluence = all_fvgs
    
    # 3. Inicializar ConfluenceAnalyzer
    print("\n🔗 INICIALIZANDO CONFLUENCE ANALYZER...")
    confluence_analyzer = ConfluenceAnalyzer(
        timeframes=timeframes,
        confluence_threshold=7.0
    )
    
    # 4. Analizar confluencias entre timeframes usando el método automático
    print("\n🎯 ANALIZANDO CONFLUENCIAS CON MÉTODO AUTOMÁTICO...")
    
    # Usar el nuevo método automático
    confluences_auto = confluence_analyzer.find_confluences(fvgs_for_confluence)
    
    print(f"🎯 {len(confluences_auto)} confluencias encontradas automáticamente")
    
    # Generar resumen
    summary = confluence_analyzer.get_confluence_summary(confluences_auto)
    
    print(f"\n📊 RESUMEN AUTOMÁTICO:")
    print(f"   • Total confluencias: {summary['total_confluences']}")
    if summary['total_confluences'] > 0:
        print(f"   • Fuerza promedio: {summary['avg_strength']:.2f}")
        print(f"   • Fuerza máxima: {summary['max_strength']:.2f}")
        print(f"   • Fuerza mínima: {summary['min_strength']:.2f}")
    
    # También hacer análisis manual como backup
    print(f"\n🔄 ANÁLISIS MANUAL DE CONFLUENCIAS...")
    
    confluences_manual = []
    total_comparisons = 0
    
    # Comparar FVGs entre diferentes timeframes (análisis limitado para demo)
    for tf1 in timeframes[:2]:  # Solo los primeros 2 timeframes para demo
        for tf2 in timeframes[:2]:
            if tf1 != tf2 and tf1 in fvgs_for_confluence and tf2 in fvgs_for_confluence:
                
                fvgs1 = fvgs_for_confluence[tf1]
                fvgs2 = fvgs_for_confluence[tf2]
                
                print(f"\n🔄 Comparando {tf1} vs {tf2}...")
                print(f"   📊 {len(fvgs1)} FVGs en {tf1}, {len(fvgs2)} FVGs en {tf2}")
                
                confluences_in_pair = 0
                
                # Analizar cada combinación (limitado para demo)
                for i, fvg1 in enumerate(fvgs1[:5]):  # Solo 5 por timeframe
                    for j, fvg2 in enumerate(fvgs2[:5]):
                        
                        strength = confluence_analyzer.analyze_confluence_strength(fvg1, fvg2)
                        total_comparisons += 1
                        
                        # Si la confluencia es fuerte
                        if strength >= confluence_analyzer.confluence_threshold:
                            confluences_manual.append({
                                'tf1': tf1,
                                'tf2': tf2,
                                'fvg1_index': i,
                                'fvg2_index': j,
                                'strength': strength,
                                'fvg1': fvg1,
                                'fvg2': fvg2
                            })
                            confluences_in_pair += 1
                
                print(f"   🎯 {confluences_in_pair} confluencias encontradas")
    
    # Usar confluencias automáticas si están disponibles, sino las manuales
    confluences_found = confluences_auto if confluences_auto else confluences_manual
    
    # 5. Reportar resultados
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE CONFLUENCIAS DETECTADAS")
    print("=" * 60)
    
    print(f"🔍 Total comparaciones realizadas: {total_comparisons}")
    print(f"🎯 Confluencias fuertes encontradas: {len(confluences_found)}")
    print(f"📈 Umbral de confluencia: {confluence_analyzer.confluence_threshold}")
    
    # Mostrar las mejores confluencias
    if confluences_found:
        print(f"\n🏆 TOP CONFLUENCIAS (por fuerza):")
        
        # Si son confluencias automáticas, tienen estructura diferente
        if confluences_auto:
            confluences_found.sort(key=lambda x: x['strength'], reverse=True)
            
            for i, conf in enumerate(confluences_found[:5]):  # Top 5
                tf1, tf2 = conf['timeframes']
                print(f"\n   {i+1}. 🎯 Confluencia {tf1} ↔ {tf2}")
                print(f"      💪 Fuerza: {conf['strength']:.2f}/10")
                fvg1, fvg2 = conf['fvgs']
                print(f"      📊 FVG {tf1}: {fvg1.type}")
                print(f"      📊 FVG {tf2}: {fvg2.type}")
                
                # Información adicional si está disponible
                if hasattr(fvg1, 'gap_size'):
                    print(f"      📏 Size {tf1}: {fvg1.gap_size:.5f}")
                if hasattr(fvg2, 'gap_size'):
                    print(f"      📏 Size {tf2}: {fvg2.gap_size:.5f}")
        else:
            # Confluencias manuales
            confluences_found.sort(key=lambda x: x['strength'], reverse=True)
            
            for i, conf in enumerate(confluences_found[:5]):  # Top 5
                print(f"\n   {i+1}. 🎯 Confluencia {conf['tf1']} ↔ {conf['tf2']}")
                print(f"      💪 Fuerza: {conf['strength']:.2f}/10")
                print(f"      📊 FVG {conf['tf1']}: {conf['fvg1'].type}")
                print(f"      📊 FVG {conf['tf2']}: {conf['fvg2'].type}")
                
                # Información adicional si está disponible
                if hasattr(conf['fvg1'], 'gap_size'):
                    print(f"      📏 Size {conf['tf1']}: {conf['fvg1'].gap_size:.5f}")
                if hasattr(conf['fvg2'], 'gap_size'):
                    print(f"      📏 Size {conf['tf2']}: {conf['fvg2'].gap_size:.5f}")
    
    else:
        print("\n⚠️ No se encontraron confluencias que superen el umbral")
        print("💡 Posibles causas:")
        print("   • Umbral muy alto (actual: 7.0)")
        print("   • Pocos FVGs en los timeframes")
        print("   • Algoritmo necesita ajuste")
    
    # 6. Sugerencias de mejora
    print(f"\n💡 SUGERENCIAS PARA MEJORAR:")
    print(f"   • Implementar cálculo real de overlap temporal")
    print(f"   • Mejorar algoritmo de overlap de precios")
    print(f"   • Agregar análisis de volumen")
    print(f"   • Implementar filtros por proximidad temporal")
    print(f"   • Crear scoring más sofisticado")
    
    print(f"\n✅ Demo completado!")

if __name__ == "__main__":
    main()
