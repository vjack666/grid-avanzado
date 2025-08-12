"""
🤖 OFICINA DE IA - PISO 3
Módulos especializados en Machine Learning y optimización automática

Componentes:
- FVGMLPredictor: Predicciones con Machine Learning
- PatternRecognizer: Reconocimiento de patrones avanzados
- AutoOptimizer: Optimización automática de parámetros
- PerformanceAnalyzer: Análisis de rendimiento con IA
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score
import joblib
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional, Tuple, Any

logger = logging.getLogger(__name__)

class FVGMLPredictor:
    """
    🎯 PREDICTOR ML PARA FVGs
    
    Sistema de Machine Learning para predecir:
    - Probabilidad de llenado de FVGs
    - Tiempo estimado de llenado
    - Dirección probable del mercado
    - Calidad esperada de FVGs futuros
    """
    
    def __init__(self, model_path=None):
        """
        Inicializa el predictor ML
        
        Args:
            model_path: Ruta para cargar modelo pre-entrenado
        """
        self.models = {
            'fill_probability': RandomForestClassifier(n_estimators=100, random_state=42),
            'time_to_fill': GradientBoostingRegressor(n_estimators=100, random_state=42),
            'direction': RandomForestClassifier(n_estimators=80, random_state=42),
            'quality': GradientBoostingRegressor(n_estimators=80, random_state=42)
        }
        
        self.scalers = {
            'features': StandardScaler(),
            'target': StandardScaler()
        }
        
        self.label_encoders = {}
        self.feature_importance = {}
        self.model_metrics = {}
        self.is_trained = False
        
        if model_path:
            self.load_models(model_path)
        
        print("🤖 FVGMLPredictor inicializado")
    
    def prepare_features(self, fvg_data, market_data=None, technical_indicators=None):
        """
        Prepara características para el modelo ML
        
        Args:
            fvg_data: Datos de FVGs
            market_data: Datos de mercado
            technical_indicators: Indicadores técnicos
            
        Returns:
            DataFrame con características preparadas
        """
        features = []
        
        for fvg in fvg_data:
            fvg_features = self._extract_fvg_features(fvg)
            
            if market_data:
                market_features = self._extract_market_features(fvg, market_data)
                fvg_features.update(market_features)
            
            if technical_indicators:
                tech_features = self._extract_technical_features(fvg, technical_indicators)
                fvg_features.update(tech_features)
            
            features.append(fvg_features)
        
        df_features = pd.DataFrame(features)
        
        # Manejar valores faltantes
        df_features = df_features.fillna(df_features.mean())
        
        return df_features
    
    def _extract_fvg_features(self, fvg):
        """Extrae características del FVG"""
        features = {}
        
        # Características básicas
        features['gap_size_pips'] = getattr(fvg, 'gap_size_pips', 0)
        features['gap_size_relative'] = getattr(fvg, 'gap_size', 0) / getattr(fvg, 'gap_high', 1) if hasattr(fvg, 'gap_high') else 0
        features['fvg_type'] = 1 if getattr(fvg, 'type', '') == 'BULLISH' else 0
        
        # Características temporales
        if hasattr(fvg, 'formation_time'):
            formation_time = pd.to_datetime(fvg.formation_time)
            features['hour'] = formation_time.hour
            features['day_of_week'] = formation_time.dayofweek
            features['is_london_session'] = 1 if 7 <= formation_time.hour <= 16 else 0
            features['is_ny_session'] = 1 if 13 <= formation_time.hour <= 22 else 0
            features['is_overlap'] = 1 if 13 <= formation_time.hour <= 16 else 0
        
        # Características de velas de formación
        if hasattr(fvg, 'formation_candles') and len(fvg.formation_candles) >= 3:
            candles = fvg.formation_candles
            middle_candle = candles[1]
            
            # Análisis de la vela de impulso
            body_size = abs(middle_candle['close'] - middle_candle['open'])
            total_range = middle_candle['high'] - middle_candle['low']
            features['impulse_body_ratio'] = body_size / total_range if total_range > 0 else 0
            features['impulse_volume'] = middle_candle.get('volume', 0)
            
            # Ratios entre velas
            prev_range = candles[0]['high'] - candles[0]['low']
            next_range = candles[2]['high'] - candles[2]['low']
            features['impulse_vs_prev_ratio'] = total_range / prev_range if prev_range > 0 else 1
            features['impulse_vs_next_ratio'] = total_range / next_range if next_range > 0 else 1
        
        return features
    
    def _extract_market_features(self, fvg, market_data):
        """Extrae características del contexto de mercado"""
        features = {}
        
        if 'trend' in market_data:
            features['market_trend'] = market_data['trend']
        
        if 'volatility' in market_data:
            features['market_volatility'] = market_data['volatility']
        
        if 'volume_profile' in market_data:
            features['volume_above_avg'] = 1 if market_data['volume_profile'] > 1.2 else 0
        
        if 'price_distance_to_fvg' in market_data:
            features['price_distance'] = market_data['price_distance_to_fvg']
        
        return features
    
    def _extract_technical_features(self, fvg, technical_indicators):
        """Extrae características de indicadores técnicos"""
        features = {}
        
        # RSI
        if 'rsi' in technical_indicators:
            rsi = technical_indicators['rsi']
            features['rsi'] = rsi
            features['rsi_oversold'] = 1 if rsi < 30 else 0
            features['rsi_overbought'] = 1 if rsi > 70 else 0
        
        # Moving Averages
        if 'sma_20' in technical_indicators and 'sma_50' in technical_indicators:
            sma_20 = technical_indicators['sma_20']
            sma_50 = technical_indicators['sma_50']
            features['sma_cross'] = 1 if sma_20 > sma_50 else 0
            features['sma_distance'] = abs(sma_20 - sma_50) / sma_50 if sma_50 > 0 else 0
        
        # MACD
        if 'macd' in technical_indicators:
            features['macd_bullish'] = 1 if technical_indicators['macd'] > 0 else 0
        
        # Bollinger Bands
        if all(key in technical_indicators for key in ['bb_upper', 'bb_lower', 'bb_middle']):
            bb_position = (fvg.gap_high - technical_indicators['bb_lower']) / \
                         (technical_indicators['bb_upper'] - technical_indicators['bb_lower'])
            features['bb_position'] = bb_position
        
        return features
    
    def train_models(self, training_data, validation_split=0.2):
        """
        Entrena todos los modelos ML
        
        Args:
            training_data: Datos de entrenamiento con features y targets
            validation_split: Proporción para validación
        """
        print("🔄 Iniciando entrenamiento de modelos ML...")
        
        # Preparar datos
        X = training_data['features']
        
        # Escalar características
        X_scaled = self.scalers['features'].fit_transform(X)
        
        # Entrenar cada modelo
        for target_name, model in self.models.items():
            if target_name in training_data['targets']:
                y = training_data['targets'][target_name]
                
                # División train/validation
                X_train, X_val, y_train, y_val = train_test_split(
                    X_scaled, y, test_size=validation_split, random_state=42
                )
                
                # Entrenamiento
                print(f"   🎯 Entrenando modelo {target_name}...")
                model.fit(X_train, y_train)
                
                # Validación
                y_pred = model.predict(X_val)
                
                # Métricas
                if target_name in ['fill_probability', 'direction']:
                    # Clasificación
                    accuracy = accuracy_score(y_val, y_pred)
                    precision = precision_score(y_val, y_pred, average='weighted')
                    recall = recall_score(y_val, y_pred, average='weighted')
                    
                    self.model_metrics[target_name] = {
                        'accuracy': accuracy,
                        'precision': precision,
                        'recall': recall
                    }
                    
                    print(f"      ✅ Accuracy: {accuracy:.3f}, Precision: {precision:.3f}, Recall: {recall:.3f}")
                
                else:
                    # Regresión
                    from sklearn.metrics import mean_squared_error, r2_score
                    mse = mean_squared_error(y_val, y_pred)
                    r2 = r2_score(y_val, y_pred)
                    
                    self.model_metrics[target_name] = {
                        'mse': mse,
                        'r2': r2
                    }
                    
                    print(f"      ✅ MSE: {mse:.3f}, R²: {r2:.3f}")
                
                # Feature importance
                if hasattr(model, 'feature_importances_'):
                    importance = model.feature_importances_
                    feature_names = X.columns
                    
                    self.feature_importance[target_name] = dict(zip(feature_names, importance))
        
        self.is_trained = True
        print("✅ Entrenamiento completado")
    
    def predict(self, fvg_data, market_context=None, return_confidence=True):
        """
        Realiza predicciones para FVGs
        
        Args:
            fvg_data: Datos de FVGs
            market_context: Contexto de mercado
            return_confidence: Si incluir niveles de confianza
            
        Returns:
            Dict con predicciones
        """
        if not self.is_trained:
            raise ValueError("Modelos no entrenados. Llamar train_models() primero.")
        
        # Preparar características
        features = self.prepare_features(fvg_data, market_context)
        X_scaled = self.scalers['features'].transform(features)
        
        predictions = {}
        
        for target_name, model in self.models.items():
            if target_name in self.model_metrics:
                pred = model.predict(X_scaled)
                predictions[target_name] = pred.tolist()
                
                if return_confidence and hasattr(model, 'predict_proba'):
                    # Para modelos de clasificación
                    proba = model.predict_proba(X_scaled)
                    confidence = np.max(proba, axis=1)
                    predictions[f'{target_name}_confidence'] = confidence.tolist()
        
        return predictions
    
    def save_models(self, save_path):
        """Guarda modelos entrenados"""
        model_data = {
            'models': self.models,
            'scalers': self.scalers,
            'label_encoders': self.label_encoders,
            'feature_importance': self.feature_importance,
            'model_metrics': self.model_metrics,
            'is_trained': self.is_trained
        }
        
        joblib.dump(model_data, save_path)
        print(f"✅ Modelos guardados en {save_path}")
    
    def load_models(self, load_path):
        """Carga modelos pre-entrenados"""
        try:
            model_data = joblib.load(load_path)
            
            self.models = model_data['models']
            self.scalers = model_data['scalers']
            self.label_encoders = model_data['label_encoders']
            self.feature_importance = model_data['feature_importance']
            self.model_metrics = model_data['model_metrics']
            self.is_trained = model_data['is_trained']
            
            print(f"✅ Modelos cargados desde {load_path}")
        
        except Exception as e:
            print(f"❌ Error cargando modelos: {e}")


class PatternRecognizer:
    """
    🔍 RECONOCEDOR DE PATRONES AVANZADOS
    
    Utiliza técnicas de ML para reconocer patrones complejos
    en formaciones de FVGs y comportamiento del mercado
    """
    
    def __init__(self):
        """Inicializa el reconocedor de patrones"""
        self.known_patterns = {}
        self.pattern_templates = []
        self.similarity_threshold = 0.75
        
        print("🔍 PatternRecognizer inicializado")
    
    def add_pattern_template(self, pattern_name, template_data, success_rate=None):
        """
        Añade un template de patrón conocido
        
        Args:
            pattern_name: Nombre del patrón
            template_data: Datos del template
            success_rate: Tasa de éxito histórica del patrón
        """
        template = {
            'name': pattern_name,
            'data': template_data,
            'success_rate': success_rate or 0.5,
            'created_at': datetime.now()
        }
        
        self.pattern_templates.append(template)
        print(f"✅ Template '{pattern_name}' añadido")
    
    def recognize_patterns(self, current_data):
        """
        Reconoce patrones en datos actuales
        
        Args:
            current_data: Datos actuales para análisis
            
        Returns:
            Lista de patrones reconocidos
        """
        recognized_patterns = []
        
        for template in self.pattern_templates:
            similarity = self._calculate_pattern_similarity(current_data, template['data'])
            
            if similarity >= self.similarity_threshold:
                pattern_match = {
                    'pattern_name': template['name'],
                    'similarity': similarity,
                    'success_rate': template['success_rate'],
                    'confidence': similarity * template['success_rate'],
                    'detected_at': datetime.now()
                }
                
                recognized_patterns.append(pattern_match)
        
        return sorted(recognized_patterns, key=lambda x: x['confidence'], reverse=True)
    
    def _calculate_pattern_similarity(self, data1, data2):
        """Calcula similitud entre dos patrones"""
        # Implementación simplificada - en producción usaría DTW o técnicas más avanzadas
        
        # Convertir a arrays numpy
        arr1 = np.array(list(data1.values()))
        arr2 = np.array(list(data2.values()))
        
        # Normalizar
        arr1_norm = (arr1 - np.mean(arr1)) / (np.std(arr1) + 1e-8)
        arr2_norm = (arr2 - np.mean(arr2)) / (np.std(arr2) + 1e-8)
        
        # Correlación
        correlation = np.corrcoef(arr1_norm, arr2_norm)[0, 1]
        
        # Convertir a similitud (0-1)
        similarity = (correlation + 1) / 2
        
        return max(0, min(1, similarity))
    
    def learn_new_pattern(self, pattern_data, outcome, pattern_name=None):
        """
        Aprende un nuevo patrón basado en datos y resultado
        
        Args:
            pattern_data: Datos del patrón
            outcome: Resultado (éxito/fallo)
            pattern_name: Nombre opcional del patrón
        """
        if not pattern_name:
            pattern_name = f"Pattern_{len(self.pattern_templates) + 1}"
        
        success_rate = 1.0 if outcome else 0.0
        
        self.add_pattern_template(pattern_name, pattern_data, success_rate)
        print(f"📚 Patrón '{pattern_name}' aprendido con tasa de éxito: {success_rate}")


class AutoOptimizer:
    """
    ⚡ OPTIMIZADOR AUTOMÁTICO
    
    Optimiza automáticamente parámetros del sistema usando
    algoritmos genéticos y optimización bayesiana
    """
    
    def __init__(self):
        """Inicializa el optimizador automático"""
        self.optimization_history = []
        self.best_parameters = {}
        self.optimization_in_progress = False
        
        print("⚡ AutoOptimizer inicializado")
    
    def optimize_detection_parameters(self, historical_data, target_metric='accuracy'):
        """
        Optimiza parámetros de detección FVG
        
        Args:
            historical_data: Datos históricos para optimización
            target_metric: Métrica objetivo a optimizar
            
        Returns:
            Dict con mejores parámetros encontrados
        """
        print(f"🔄 Iniciando optimización de parámetros (objetivo: {target_metric})")
        
        # Espacio de parámetros a optimizar
        parameter_space = {
            'min_gap_size': [0.00001, 0.00005, 0.0001, 0.0002],
            'min_body_ratio': [0.5, 0.6, 0.65, 0.7, 0.75],
            'confluence_threshold': [5.0, 6.0, 7.0, 8.0, 9.0],
            'session_weight': [0.1, 0.2, 0.3, 0.4]
        }
        
        best_score = 0
        best_params = {}
        
        # Grid search simplificado (en producción usaría optimización bayesiana)
        total_combinations = np.prod([len(values) for values in parameter_space.values()])
        print(f"   Evaluando {total_combinations} combinaciones...")
        
        combination_count = 0
        
        import itertools
        
        for params in itertools.product(*parameter_space.values()):
            param_dict = dict(zip(parameter_space.keys(), params))
            
            # Evaluar parámetros
            score = self._evaluate_parameters(param_dict, historical_data, target_metric)
            
            if score > best_score:
                best_score = score
                best_params = param_dict.copy()
                print(f"   🎯 Nuevo mejor score: {score:.3f} con {param_dict}")
            
            combination_count += 1
            
            if combination_count % 20 == 0:
                progress = (combination_count / total_combinations) * 100
                print(f"   📊 Progreso: {progress:.1f}%")
        
        self.best_parameters = best_params
        
        optimization_result = {
            'best_parameters': best_params,
            'best_score': best_score,
            'total_evaluated': combination_count,
            'optimization_date': datetime.now()
        }
        
        self.optimization_history.append(optimization_result)
        
        print(f"✅ Optimización completada. Mejor score: {best_score:.3f}")
        return optimization_result
    
    def _evaluate_parameters(self, parameters, historical_data, target_metric):
        """Evalúa un conjunto de parámetros"""
        # Simulación de evaluación (en producción correría backtest completo)
        
        # Factores que afectan el score
        gap_size_factor = 1.0 - abs(parameters['min_gap_size'] - 0.00005) / 0.0002
        body_ratio_factor = 1.0 - abs(parameters['min_body_ratio'] - 0.65) / 0.25
        confluence_factor = 1.0 - abs(parameters['confluence_threshold'] - 7.0) / 4.0
        session_factor = 1.0 - abs(parameters['session_weight'] - 0.25) / 0.35
        
        # Score combinado con ruido aleatorio para simular variabilidad real
        base_score = (gap_size_factor + body_ratio_factor + confluence_factor + session_factor) / 4
        noise = np.random.normal(0, 0.05)  # 5% de ruido
        
        final_score = max(0, min(1, base_score + noise))
        
        return final_score
    
    def get_optimization_summary(self):
        """Obtiene resumen de optimizaciones realizadas"""
        if not self.optimization_history:
            return {"message": "No hay optimizaciones realizadas"}
        
        latest = self.optimization_history[-1]
        
        return {
            'total_optimizations': len(self.optimization_history),
            'latest_optimization': latest['optimization_date'],
            'best_score_achieved': latest['best_score'],
            'current_best_parameters': self.best_parameters,
            'improvement_over_time': self._calculate_improvement_trend()
        }
    
    def _calculate_improvement_trend(self):
        """Calcula tendencia de mejora a lo largo del tiempo"""
        if len(self.optimization_history) < 2:
            return 0
        
        scores = [opt['best_score'] for opt in self.optimization_history]
        first_score = scores[0]
        last_score = scores[-1]
        
        improvement = ((last_score - first_score) / first_score) * 100
        return improvement


class PerformanceAnalyzer:
    """
    📊 ANALIZADOR DE RENDIMIENTO CON IA
    
    Analiza el rendimiento del sistema usando técnicas de IA
    para identificar áreas de mejora y optimización
    """
    
    def __init__(self):
        """Inicializa el analizador de rendimiento"""
        self.performance_metrics = {}
        self.analysis_history = []
        
        print("📊 PerformanceAnalyzer inicializado")
    
    def analyze_system_performance(self, performance_data, period_days=30):
        """
        Analiza el rendimiento general del sistema
        
        Args:
            performance_data: Datos de rendimiento
            period_days: Período de análisis en días
            
        Returns:
            Dict con análisis completo
        """
        print(f"📈 Analizando rendimiento de los últimos {period_days} días...")
        
        analysis = {
            'period_days': period_days,
            'analysis_date': datetime.now(),
            'detection_performance': self._analyze_detection_performance(performance_data),
            'prediction_accuracy': self._analyze_prediction_accuracy(performance_data),
            'system_efficiency': self._analyze_system_efficiency(performance_data),
            'recommendations': self._generate_recommendations(performance_data)
        }
        
        self.analysis_history.append(analysis)
        
        return analysis
    
    def _analyze_detection_performance(self, data):
        """Analiza rendimiento de detección"""
        detection_metrics = {
            'total_detections': data.get('total_fvgs_detected', 0),
            'detection_rate': data.get('detection_rate', 0),
            'false_positive_rate': data.get('false_positives', 0) / max(1, data.get('total_detections', 1)),
            'average_detection_time': data.get('avg_detection_time_ms', 0),
            'quality_distribution': data.get('quality_distribution', {})
        }
        
        # Score de rendimiento de detección
        detection_score = self._calculate_detection_score(detection_metrics)
        detection_metrics['performance_score'] = detection_score
        
        return detection_metrics
    
    def _analyze_prediction_accuracy(self, data):
        """Analiza precisión de predicciones"""
        prediction_metrics = {
            'fill_prediction_accuracy': data.get('fill_prediction_accuracy', 0),
            'direction_prediction_accuracy': data.get('direction_accuracy', 0),
            'time_prediction_mae': data.get('time_prediction_mae', 0),
            'confidence_calibration': data.get('confidence_calibration', 0)
        }
        
        # Score de precisión de predicciones
        prediction_score = self._calculate_prediction_score(prediction_metrics)
        prediction_metrics['performance_score'] = prediction_score
        
        return prediction_metrics
    
    def _analyze_system_efficiency(self, data):
        """Analiza eficiencia del sistema"""
        efficiency_metrics = {
            'cpu_usage_avg': data.get('cpu_usage_avg', 0),
            'memory_usage_avg': data.get('memory_usage_avg', 0),
            'processing_latency': data.get('processing_latency_ms', 0),
            'throughput': data.get('fvgs_per_second', 0),
            'error_rate': data.get('error_rate', 0)
        }
        
        # Score de eficiencia
        efficiency_score = self._calculate_efficiency_score(efficiency_metrics)
        efficiency_metrics['performance_score'] = efficiency_score
        
        return efficiency_metrics
    
    def _calculate_detection_score(self, metrics):
        """Calcula score de detección (0-100)"""
        detection_rate = min(100, metrics['detection_rate'] * 100)
        false_positive_penalty = metrics['false_positive_rate'] * 50
        speed_bonus = max(0, (1000 - metrics['average_detection_time']) / 10)
        
        score = detection_rate - false_positive_penalty + speed_bonus
        return max(0, min(100, score))
    
    def _calculate_prediction_score(self, metrics):
        """Calcula score de predicción (0-100)"""
        fill_accuracy = metrics['fill_prediction_accuracy'] * 50
        direction_accuracy = metrics['direction_prediction_accuracy'] * 30
        calibration_bonus = metrics['confidence_calibration'] * 20
        
        score = fill_accuracy + direction_accuracy + calibration_bonus
        return max(0, min(100, score))
    
    def _calculate_efficiency_score(self, metrics):
        """Calcula score de eficiencia (0-100)"""
        cpu_penalty = metrics['cpu_usage_avg'] * 0.5
        memory_penalty = metrics['memory_usage_avg'] * 0.3
        latency_penalty = metrics['processing_latency'] * 0.01
        throughput_bonus = min(50, metrics['throughput'] * 10)
        error_penalty = metrics['error_rate'] * 100
        
        score = 100 - cpu_penalty - memory_penalty - latency_penalty + throughput_bonus - error_penalty
        return max(0, min(100, score))
    
    def _generate_recommendations(self, data):
        """Genera recomendaciones de mejora"""
        recommendations = []
        
        # Análisis de detección
        if data.get('false_positive_rate', 0) > 0.1:
            recommendations.append({
                'category': 'DETECTION',
                'priority': 'HIGH',
                'description': 'Alta tasa de falsos positivos detectada',
                'action': 'Ajustar parámetros de detección o mejorar filtros'
            })
        
        # Análisis de predicción
        if data.get('fill_prediction_accuracy', 0) < 0.7:
            recommendations.append({
                'category': 'PREDICTION',
                'priority': 'MEDIUM',
                'description': 'Precisión de predicción de llenado baja',
                'action': 'Re-entrenar modelos ML con más datos'
            })
        
        # Análisis de eficiencia
        if data.get('processing_latency_ms', 0) > 500:
            recommendations.append({
                'category': 'EFFICIENCY',
                'priority': 'HIGH',
                'description': 'Latencia de procesamiento alta',
                'action': 'Optimizar algoritmos o actualizar hardware'
            })
        
        # Análisis de recursos
        if data.get('cpu_usage_avg', 0) > 80:
            recommendations.append({
                'category': 'RESOURCES',
                'priority': 'MEDIUM',
                'description': 'Uso de CPU elevado',
                'action': 'Optimizar código o distribuir carga'
            })
        
        return recommendations
    
    def get_performance_trend(self, metric_name, days=7):
        """Obtiene tendencia de una métrica específica"""
        recent_analyses = [
            analysis for analysis in self.analysis_history 
            if (datetime.now() - analysis['analysis_date']).days <= days
        ]
        
        if len(recent_analyses) < 2:
            return {"trend": "INSUFFICIENT_DATA"}
        
        # Extraer valores de la métrica
        values = []
        for analysis in recent_analyses:
            # Navegar por la estructura anidada para encontrar la métrica
            value = self._extract_metric_value(analysis, metric_name)
            if value is not None:
                values.append(value)
        
        if len(values) < 2:
            return {"trend": "INSUFFICIENT_DATA"}
        
        # Calcular tendencia
        if values[-1] > values[0]:
            trend = "IMPROVING"
        elif values[-1] < values[0]:
            trend = "DECLINING"
        else:
            trend = "STABLE"
        
        return {
            "trend": trend,
            "change_percentage": ((values[-1] - values[0]) / values[0]) * 100 if values[0] != 0 else 0,
            "current_value": values[-1],
            "previous_value": values[0]
        }
    
    def _extract_metric_value(self, analysis, metric_name):
        """Extrae valor de métrica del análisis"""
        # Buscar en todas las categorías
        for category in ['detection_performance', 'prediction_accuracy', 'system_efficiency']:
            if category in analysis and metric_name in analysis[category]:
                return analysis[category][metric_name]
        return None


# Configuración de la oficina de IA
IA_CONFIG = {
    "ml_predictor": {
        "model_types": ["RandomForest", "GradientBoosting"],
        "validation_split": 0.2,
        "feature_importance_threshold": 0.01
    },
    "pattern_recognizer": {
        "similarity_threshold": 0.75,
        "max_patterns": 100,
        "learning_rate": 0.1
    },
    "auto_optimizer": {
        "optimization_method": "grid_search",  # "bayesian", "genetic"
        "max_iterations": 100,
        "convergence_threshold": 0.001
    },
    "performance_analyzer": {
        "analysis_frequency": "daily",
        "retention_days": 90,
        "alert_thresholds": {
            "detection_score": 70,
            "prediction_score": 65,
            "efficiency_score": 75
        }
    }
}

__all__ = [
    "FVGMLPredictor",
    "PatternRecognizer",
    "AutoOptimizer", 
    "PerformanceAnalyzer",
    "IA_CONFIG"
]
