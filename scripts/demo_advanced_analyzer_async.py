"""
🚀 DEMO AVANZADO - ADVANCED ANALYZER ASÍNCRONO
==============================================

Demostración en vivo del AdvancedAnalyzer con datos asíncronos
Sistema de análisis ML y estadístico optimizado para velocidad

PUERTA: PUERTA-S2-ANALYZER
VERSIÓN: v1.0.0
FECHA: 2025-08-11
"""

import asyncio
import sys
import os
import time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Agregar path del proyecto
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.core.config_manager import ConfigManager
from src.core.logger_manager import LoggerManager
from src.core.error_manager import ErrorManager
from src.core.data_manager import DataManager
from src.core.real_time.advanced_analyzer import AdvancedAnalyzer

class AdvancedAnalyzerDemo:
    """Demo interactivo del AdvancedAnalyzer asíncrono"""
    
    def __init__(self):
        """Inicializar demo"""
        print("🚀 INICIALIZANDO ADVANCED ANALYZER DEMO")
        print("=" * 50)
        
        # Inicializar managers
        self.config = ConfigManager()
        self.logger = LoggerManager()
        self.error = ErrorManager(self.logger, self.config)
        self.data = DataManager(self.config, self.logger, self.error)
        
        # Inicializar AdvancedAnalyzer
        self.analyzer = AdvancedAnalyzer(
            config=self.config,
            logger=self.logger,
            error=self.error,
            data_manager=self.data
        )
        
        print(f"✅ {self.analyzer.component_id} {self.analyzer.version} inicializado")
        print(f"📊 Análisis ML disponible: {self.analyzer.analyzer_config['ml_enabled']}")
        print()
    
    async def demo_analisis_asincrono(self):
        """Demo de análisis asíncrono"""
        print("🔄 INICIANDO ANÁLISIS ASÍNCRONO")
        print("-" * 30)
        
        # Configurar para demo rápido
        self.analyzer.analyzer_config["analysis_interval_minutes"] = 0.05  # 3 segundos
        
        # Iniciar servicio asíncrono
        await self.analyzer.start_async_analysis_service()
        
        print("⏱️  Ejecutando análisis concurrentes...")
        
        # Permitir que se ejecuten algunos ciclos
        await asyncio.sleep(10)
        
        # Detener servicio
        self.analyzer.stop_analysis_service()
        
        print("✅ Análisis asíncrono completado")
        print()
        
        return self.analyzer.get_analysis_summary()
    
    async def demo_analisis_paralelo(self):
        """Demo de análisis paralelo con múltiples instrumentos"""
        print("🎯 DEMO ANÁLISIS PARALELO ML")
        print("-" * 30)
        
        instrumentos = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD"]
        
        # Crear tareas paralelas para cada instrumento
        tasks = []
        for instrumento in instrumentos:
            task = self._analizar_instrumento_async(instrumento)
            tasks.append(task)
        
        # Ejecutar todos los análisis concurrentemente
        start_time = time.time()
        resultados = await asyncio.gather(*tasks, return_exceptions=True)
        execution_time = time.time() - start_time
        
        print(f"⚡ Análisis paralelo completado en {execution_time:.2f}s")
        print(f"📈 Instrumentos analizados: {len(instrumentos)}")
        
        # Mostrar resultados
        for i, resultado in enumerate(resultados):
            if not isinstance(resultado, Exception):
                status = resultado.get('status', 'unknown') if isinstance(resultado, dict) else 'completed'
                print(f"  ✅ {instrumentos[i]}: {status}")
            else:
                print(f"  ❌ {instrumentos[i]}: Error - {str(resultado)}")
        
        print()
        return resultados
    
    async def _analizar_instrumento_async(self, instrumento: str):
        """Análisis asíncrono de un instrumento específico"""
        try:
            # Simular carga de datos asíncrona
            await asyncio.sleep(0.1)
            
            # Simular análisis de correlaciones
            await self.analyzer._async_correlation_analysis()
            
            # Simular análisis de volatilidad
            await self.analyzer._async_volatility_analysis()
            
            # Simular predicciones ML si están disponibles
            if self.analyzer.analyzer_config["ml_enabled"]:
                await self.analyzer._async_ml_predictions()
            
            # Simular análisis de microestructura
            await self.analyzer._async_microstructure_analysis()
            
            return {
                "instrumento": instrumento,
                "status": "completado",
                "timestamp": datetime.now(),
                "analyses": ["correlation", "volatility", "ml_prediction", "microstructure"]
            }
            
        except Exception as e:
            return {"instrumento": instrumento, "status": "error", "error": str(e)}
    
    def demo_status_completo(self):
        """Demo del estado completo del analyzer"""
        print("📊 ESTADO COMPLETO DEL ANALYZER")
        print("-" * 35)
        
        status = self.analyzer.get_analyzer_status()
        summary = self.analyzer.get_analysis_summary()
        
        # Información básica
        print(f"🏷️  ID: {status['component_id']}")
        print(f"📦 Versión: {status['version']}")
        print(f"⚡ Estado: {status['status']}")
        print(f"🔄 Análisis activo: {status['is_analyzing']}")
        print()
        
        # Métricas de rendimiento
        print("📈 MÉTRICAS DE RENDIMIENTO:")
        print(f"  • Total análisis: {summary['total_analyses']}")
        print(f"  • Tasa éxito: {summary['success_rate']:.1f}%")
        print(f"  • Tiempo promedio: {summary['average_analysis_time']:.3f}s")
        print(f"  • Correlaciones: {summary['correlations_calculated']}")
        print(f"  • Predicciones ML: {summary['ml_predictions_made']}")
        print(f"  • Anomalías detectadas: {summary['anomalies_detected']}")
        print()
        
        # Configuración activa
        print("⚙️  CONFIGURACIÓN ACTIVA:")
        config = status['configuration']
        print(f"  • Análisis ML: {config['ml_enabled']}")
        print(f"  • Análisis microestructura: {config['microstructure_enabled']}")
        print(f"  • Detección anomalías: {config['anomaly_detection_enabled']}")
        print(f"  • Intervalo análisis: {config['analysis_interval_minutes']} min")
        print()
        
        # Estructuras de datos
        print("🗄️  ESTRUCTURAS DE DATOS:")
        data_structures = status['data_structures']
        print(f"  • Historial correlaciones: {data_structures['correlation_history_size']}")
        print(f"  • Clusters volatilidad: {data_structures['volatility_clusters_size']}")
        print(f"  • Patrones estacionales: {data_structures['seasonal_patterns_count']}")
        print(f"  • Predicciones ML: {data_structures['ml_predictions_size']}")
        print(f"  • Datos microestructura: {data_structures['microstructure_data_size']}")
        print()
        
        return status, summary
    
    async def demo_benchmark_velocidad(self):
        """Demo de benchmark de velocidad síncrono vs asíncrono"""
        print("🏃‍♂️ BENCHMARK: SÍNCRONO vs ASÍNCRONO")
        print("-" * 40)
        
        num_iterations = 100
        
        # Test síncrono
        print("🔄 Ejecutando análisis síncronos...")
        start_time = time.time()
        for i in range(num_iterations):
            self.analyzer._update_correlation_analysis()
            self.analyzer._update_volatility_analysis()
            if i % 20 == 0:
                print(f"  Progreso síncrono: {i+1}/{num_iterations}")
        
        sync_time = time.time() - start_time
        
        # Test asíncrono
        print("⚡ Ejecutando análisis asíncronos...")
        start_time = time.time()
        
        tasks = []
        for i in range(num_iterations):
            tasks.append(self.analyzer._async_correlation_analysis())
            tasks.append(self.analyzer._async_volatility_analysis())
            
            if len(tasks) >= 40:  # Procesar en lotes
                await asyncio.gather(*tasks)
                tasks = []
                print(f"  Progreso asíncrono: {i+1}/{num_iterations}")
        
        if tasks:  # Procesar lote final
            await asyncio.gather(*tasks)
        
        async_time = time.time() - start_time
        
        # Resultados
        speedup = sync_time / async_time
        print()
        print("📊 RESULTADOS DEL BENCHMARK:")
        print(f"  🐌 Tiempo síncrono: {sync_time:.3f}s")
        print(f"  ⚡ Tiempo asíncrono: {async_time:.3f}s")
        print(f"  🚀 Aceleración: {speedup:.2f}x más rápido")
        print(f"  📈 Mejora: {((speedup-1)*100):.1f}% más eficiente")
        print()
        
        return {
            "sync_time": sync_time,
            "async_time": async_time,
            "speedup": speedup,
            "iterations": num_iterations
        }

async def main():
    """Función principal del demo"""
    print("🎯 ADVANCED ANALYZER - DEMO ASÍNCRONO COMPLETO")
    print("=" * 55)
    print("Sistema de análisis ML optimizado para velocidad y concurrencia")
    print()
    
    try:
        # Inicializar demo
        demo = AdvancedAnalyzerDemo()
        
        # 1. Demo estado inicial
        print("1️⃣ ESTADO INICIAL DEL SISTEMA")
        demo.demo_status_completo()
        
        # 2. Demo análisis asíncrono
        print("2️⃣ ANÁLISIS ASÍNCRONO EN TIEMPO REAL")
        summary = await demo.demo_analisis_asincrono()
        print(f"📊 Análisis completados: {summary.get('total_analyses', 0) if summary else 0}")
        
        # 3. Demo análisis paralelo
        print("3️⃣ ANÁLISIS PARALELO MULTI-INSTRUMENTO")
        resultados = await demo.demo_analisis_paralelo()
        successful_analyses = len([r for r in resultados if isinstance(r, dict) and r.get('status') == 'completado'])
        print(f"✅ Análisis exitosos: {successful_analyses}/{len(resultados)}")
        
        # 4. Demo benchmark velocidad
        print("4️⃣ BENCHMARK DE RENDIMIENTO")
        benchmark = await demo.demo_benchmark_velocidad()
        
        # Mostrar resumen del benchmark
        print("📊 RESUMEN DEL BENCHMARK:")
        print(f"   ⚡ Aceleración: {benchmark['speedup']:.2f}x más rápido")
        print(f"   🔄 Iteraciones: {benchmark['iterations']}")
        print(f"   ⏱️ Tiempo asíncrono: {benchmark['async_time']:.3f}s")
        print(f"   📈 Eficiencia: +{((benchmark['speedup']-1)*100):.1f}%")
        print()
        
        # 5. Estado final
        print("5️⃣ ESTADO FINAL DEL SISTEMA")
        demo.demo_status_completo()
        
        print("✅ DEMO COMPLETADO EXITOSAMENTE")
        print("=" * 55)
        print("🚀 AdvancedAnalyzer listo para producción!")
        print("⚡ Rendimiento asíncrono optimizado para ML")
        print("🎯 Sistema robusto y escalable")
        
    except Exception as e:
        print(f"❌ Error en demo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Ejecutar demo asíncrono
    asyncio.run(main())
