"""
🏢 PISO 3 - OFICINA INTEGRACIÓN
Sistema Orquestador del Piso 3 - Coordinación completa de FVG Analysis + ML + Trading
"""

import sys
from pathlib import Path
import asyncio
import pandas as pd
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json

# Configurar rutas
current_dir = Path(__file__).parent
project_root = current_dir.parents[3]
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src" / "core"))
sys.path.insert(0, str(project_root / "src" / "analysis" / "piso_3"))

# Imports centralizados
from data_manager import DataManager
from logger_manager import LoggerManager

# Imports del Piso 3
try:
    from deteccion.fvg_detector import FVGDetector
    from analisis.fvg_quality_analyzer import FVGQualityAnalyzer, FVGQuality
    from ia.fvg_ml_predictor import FVGMLPredictor, FVGPrediction
    from trading.fvg_signal_generator import FVGSignalGenerator, SignalStrength
except ImportError as e:
    print(f"⚠️ Algunos componentes del Piso 3 no están disponibles: {e}")
    FVGDetector = None
    FVGQualityAnalyzer = None
    FVGMLPredictor = None
    FVGSignalGenerator = None

@dataclass
class FVGProcessingResult:
    """Resultado completo del procesamiento FVG"""
    fvg_id: str
    detection_data: Dict
    quality_analysis: Optional[Any]
    ml_prediction: Optional[Any]
    trading_signal: Optional[Any]
    processing_time: float
    timestamp: datetime
    status: str

class SystemOrchestrator:
    """
    Orquestador central del Piso 3
    
    FUNCIONES:
    1. Coordina detección de FVGs
    2. Procesa análisis de calidad
    3. Ejecuta predicciones ML
    4. Genera señales de trading
    5. Monitorea rendimiento
    6. Gestiona pipeline completo
    """
    
    def __init__(self):
        self.logger = LoggerManager().get_logger("SystemOrchestrator")
        self.data_manager = DataManager()
        
        # Inicializar componentes del Piso 3
        self.detector = FVGDetector() if FVGDetector else None
        self.quality_analyzer = FVGQualityAnalyzer() if FVGQualityAnalyzer else None
        self.ml_predictor = FVGMLPredictor() if FVGMLPredictor else None
        self.signal_generator = FVGSignalGenerator() if FVGSignalGenerator else None
        
        # Estado del sistema
        self.is_running = False
        self.processing_queue = []
        self.results_history = []
        self.performance_metrics = {
            'total_fvgs_processed': 0,
            'quality_filtered': 0,
            'ml_filtered': 0,
            'signals_generated': 0,
            'processing_time_avg': 0.0
        }
        
        # Configuración del pipeline
        self.config = {
            'min_quality_threshold': 0.6,
            'min_ml_probability': 0.55,
            'max_signals_per_hour': 5,
            'processing_interval_seconds': 30,
            'enable_quality_filter': True,
            'enable_ml_filter': True,
            'enable_signal_generation': True
        }
        
        self.logger.info("SystemOrchestrator inicializado")

    async def start_processing_pipeline(self, symbol: str = "EURUSD"):
        """
        Inicia el pipeline completo de procesamiento FVG
        
        Args:
            symbol: Símbolo del instrumento a procesar
        """
        try:
            self.is_running = True
            self.logger.info(f"🏢 PISO 3 - Pipeline iniciado para {symbol}")
            
            while self.is_running:
                start_time = datetime.now()
                
                # 1. Detectar nuevos FVGs
                new_fvgs = await self._detect_new_fvgs(symbol)
                
                if new_fvgs:
                    self.logger.info(f"Detectados {len(new_fvgs)} nuevos FVGs")
                    
                    # 2. Procesar cada FVG a través del pipeline
                    for fvg_data in new_fvgs:
                        result = await self._process_fvg_pipeline(fvg_data, symbol)
                        if result:
                            self.results_history.append(result)
                            
                            # Limpiar historial (mantener últimos 1000)
                            if len(self.results_history) > 1000:
                                self.results_history = self.results_history[-1000:]
                
                # 3. Actualizar métricas de rendimiento
                self._update_performance_metrics()
                
                # 4. Log de estado del sistema
                self._log_system_status()
                
                # Esperar antes del siguiente ciclo
                processing_time = (datetime.now() - start_time).total_seconds()
                sleep_time = max(0, self.config['processing_interval_seconds'] - processing_time)
                
                await asyncio.sleep(sleep_time)
                
        except Exception as e:
            self.logger.error(f"Error en pipeline de procesamiento: {e}")
            self.is_running = False

    async def _detect_new_fvgs(self, symbol: str) -> List[Dict]:
        """Detecta nuevos FVGs usando el detector"""
        try:
            if not self.detector:
                self.logger.warning("FVGDetector no disponible")
                return []
            
            # Obtener datos recientes
            df_m15 = self.data_manager.get_ohlc_data(symbol, 'M15', 100)
            if df_m15 is None:
                return []
            
            # Detectar FVGs
            fvgs = self.detector.detect_fvgs(df_m15, timeframe='M15')
            
            # Filtrar solo FVGs nuevos (últimas 2 horas)
            cutoff_time = datetime.now() - timedelta(hours=2)
            new_fvgs = []
            
            for fvg in fvgs:
                fvg_time = fvg.get('detection_time', datetime.now())
                if isinstance(fvg_time, str):
                    fvg_time = pd.to_datetime(fvg_time)
                    
                if fvg_time > cutoff_time:
                    new_fvgs.append(fvg)
            
            return new_fvgs
            
        except Exception as e:
            self.logger.error(f"Error detectando FVGs: {e}")
            return []

    async def _process_fvg_pipeline(self, fvg_data: Dict, symbol: str) -> Optional[FVGProcessingResult]:
        """
        Procesa un FVG a través del pipeline completo
        
        Pipeline:
        FVG Detection → Quality Analysis → ML Prediction → Signal Generation
        """
        start_time = datetime.now()
        fvg_id = fvg_data.get('id', f"fvg_{start_time.strftime('%Y%m%d_%H%M%S')}")
        
        try:
            # Inicializar resultado
            result = FVGProcessingResult(
                fvg_id=fvg_id,
                detection_data=fvg_data,
                quality_analysis=None,
                ml_prediction=None,
                trading_signal=None,
                processing_time=0.0,
                timestamp=start_time,
                status="PROCESSING"
            )
            
            # ETAPA 1: Análisis de Calidad
            if self.config['enable_quality_filter'] and self.quality_analyzer:
                quality_result = self.quality_analyzer.analyze_fvg_quality(fvg_data, symbol)
                result.quality_analysis = quality_result
                
                # Filtrar por calidad mínima
                if quality_result.score_total < self.config['min_quality_threshold']:
                    result.status = "FILTERED_QUALITY"
                    self.performance_metrics['quality_filtered'] += 1
                    self.logger.debug(f"FVG {fvg_id} filtrado por baja calidad: {quality_result.score_total:.3f}")
                    return result
            
            # ETAPA 2: Predicción ML
            if self.config['enable_ml_filter'] and self.ml_predictor:
                ml_result = self.ml_predictor.predict_fvg_fill(fvg_data, symbol)
                result.ml_prediction = ml_result
                
                # Filtrar por probabilidad ML mínima
                if ml_result.probability < self.config['min_ml_probability']:
                    result.status = "FILTERED_ML"
                    self.performance_metrics['ml_filtered'] += 1
                    self.logger.debug(f"FVG {fvg_id} filtrado por baja probabilidad ML: {ml_result.probability:.3f}")
                    return result
            
            # ETAPA 3: Generación de Señal
            if self.config['enable_signal_generation'] and self.signal_generator:
                # Verificar límite de señales por hora
                if self._check_signal_rate_limit():
                    trading_signal = self.signal_generator.generate_signal_from_fvg(fvg_data, symbol)
                    result.trading_signal = trading_signal
                    
                    if trading_signal:
                        result.status = "SIGNAL_GENERATED"
                        self.performance_metrics['signals_generated'] += 1
                        self.logger.info(f"🎯 Señal generada para FVG {fvg_id}: {trading_signal.signal_type.value}")
                    else:
                        result.status = "NO_SIGNAL"
                else:
                    result.status = "RATE_LIMITED"
                    self.logger.debug(f"FVG {fvg_id} limitado por rate limit de señales")
            
            # Finalizar resultado
            result.processing_time = (datetime.now() - start_time).total_seconds()
            result.status = result.status if result.status != "PROCESSING" else "COMPLETED"
            
            self.performance_metrics['total_fvgs_processed'] += 1
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error procesando FVG {fvg_id}: {e}")
            result.status = "ERROR"
            result.processing_time = (datetime.now() - start_time).total_seconds()
            return result

    def _check_signal_rate_limit(self) -> bool:
        """Verifica si se puede generar una nueva señal según el rate limit"""
        try:
            now = datetime.now()
            hour_ago = now - timedelta(hours=1)
            
            # Contar señales generadas en la última hora
            signals_last_hour = sum(
                1 for result in self.results_history
                if result.timestamp > hour_ago and result.trading_signal is not None
            )
            
            return signals_last_hour < self.config['max_signals_per_hour']
            
        except Exception as e:
            self.logger.error(f"Error verificando rate limit: {e}")
            return False

    def _update_performance_metrics(self):
        """Actualiza métricas de rendimiento del sistema"""
        try:
            if len(self.results_history) > 0:
                # Tiempo promedio de procesamiento
                processing_times = [r.processing_time for r in self.results_history[-100:]]
                self.performance_metrics['processing_time_avg'] = sum(processing_times) / len(processing_times)
                
        except Exception as e:
            self.logger.error(f"Error actualizando métricas: {e}")

    def _log_system_status(self):
        """Log del estado actual del sistema"""
        try:
            status = {
                'timestamp': datetime.now().isoformat(),
                'system_running': self.is_running,
                'components_status': {
                    'detector': self.detector is not None,
                    'quality_analyzer': self.quality_analyzer is not None,
                    'ml_predictor': self.ml_predictor is not None,
                    'signal_generator': self.signal_generator is not None
                },
                'performance': self.performance_metrics,
                'recent_results': len([r for r in self.results_history if r.timestamp > datetime.now() - timedelta(minutes=30)])
            }
            
            self.logger.info(f"📊 Estado del Sistema: {json.dumps(status, indent=2)}")
            
        except Exception as e:
            self.logger.error(f"Error logging estado del sistema: {e}")

    def stop_processing(self):
        """Detiene el pipeline de procesamiento"""
        self.is_running = False
        self.logger.info("🛑 Pipeline de procesamiento detenido")

    def get_system_summary(self) -> Dict:
        """Obtiene resumen completo del estado del sistema"""
        try:
            now = datetime.now()
            last_hour = now - timedelta(hours=1)
            last_24h = now - timedelta(hours=24)
            
            # Filtrar resultados por tiempo
            results_1h = [r for r in self.results_history if r.timestamp > last_hour]
            results_24h = [r for r in self.results_history if r.timestamp > last_24h]
            
            summary = {
                'system_info': {
                    'status': 'RUNNING' if self.is_running else 'STOPPED',
                    'uptime_hours': 0,  # Esto se calcularía con un timestamp de inicio
                    'components_active': sum([
                        self.detector is not None,
                        self.quality_analyzer is not None,
                        self.ml_predictor is not None,
                        self.signal_generator is not None
                    ])
                },
                'performance_1h': {
                    'fvgs_processed': len(results_1h),
                    'signals_generated': len([r for r in results_1h if r.trading_signal]),
                    'avg_processing_time': sum(r.processing_time for r in results_1h) / len(results_1h) if results_1h else 0
                },
                'performance_24h': {
                    'fvgs_processed': len(results_24h),
                    'signals_generated': len([r for r in results_24h if r.trading_signal]),
                    'quality_filter_rate': len([r for r in results_24h if r.status == 'FILTERED_QUALITY']) / len(results_24h) if results_24h else 0,
                    'ml_filter_rate': len([r for r in results_24h if r.status == 'FILTERED_ML']) / len(results_24h) if results_24h else 0
                },
                'current_config': self.config,
                'total_metrics': self.performance_metrics
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error generando resumen del sistema: {e}")
            return {}

    def get_recent_signals(self, hours: int = 24) -> List[Any]:
        """Obtiene señales generadas en las últimas horas"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            signals = []
            for result in self.results_history:
                if result.timestamp > cutoff_time and result.trading_signal:
                    signals.append(result.trading_signal)
            
            return signals
            
        except Exception as e:
            self.logger.error(f"Error obteniendo señales recientes: {e}")
            return []

    def update_config(self, new_config: Dict):
        """Actualiza configuración del sistema"""
        try:
            self.config.update(new_config)
            self.logger.info(f"Configuración actualizada: {new_config}")
        except Exception as e:
            self.logger.error(f"Error actualizando configuración: {e}")

    async def run_single_analysis(self, symbol: str = "EURUSD") -> Dict:
        """
        Ejecuta un análisis único del pipeline para testing
        
        Args:
            symbol: Símbolo a analizar
            
        Returns:
            Resultado del análisis
        """
        try:
            self.logger.info(f"🔍 Ejecutando análisis único para {symbol}")
            
            # Detectar FVGs actuales
            fvgs = await self._detect_new_fvgs(symbol)
            
            if not fvgs:
                return {
                    'status': 'NO_FVGS_DETECTED',
                    'message': 'No se detectaron FVGs en el período actual',
                    'timestamp': datetime.now().isoformat()
                }
            
            # Procesar primer FVG encontrado
            result = await self._process_fvg_pipeline(fvgs[0], symbol)
            
            return {
                'status': 'SUCCESS',
                'fvg_processed': result.fvg_id,
                'processing_time': result.processing_time,
                'final_status': result.status,
                'has_quality_analysis': result.quality_analysis is not None,
                'has_ml_prediction': result.ml_prediction is not None,
                'has_trading_signal': result.trading_signal is not None,
                'quality_score': result.quality_analysis.score_total if result.quality_analysis else None,
                'ml_probability': result.ml_prediction.probability if result.ml_prediction else None,
                'signal_type': result.trading_signal.signal_type.value if result.trading_signal else None,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error en análisis único: {e}")
            return {
                'status': 'ERROR',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }


async def main():
    """Función principal para testing del orquestador"""
    print("🏢 PISO 3 - SISTEMA ORQUESTADOR")
    print("Inicializando componentes...")
    
    orchestrator = SystemOrchestrator()
    
    # Test de análisis único
    print("\n🔍 Ejecutando análisis único...")
    result = await orchestrator.run_single_analysis()
    
    print("📊 Resultado del análisis:")
    for key, value in result.items():
        print(f"  {key}: {value}")
    
    # Mostrar resumen del sistema
    print("\n📈 Resumen del sistema:")
    summary = orchestrator.get_system_summary()
    
    for section, data in summary.items():
        print(f"\n{section}:")
        if isinstance(data, dict):
            for key, value in data.items():
                print(f"  {key}: {value}")
        else:
            print(f"  {data}")


if __name__ == "__main__":
    # Ejecutar test del orquestador
    asyncio.run(main())
