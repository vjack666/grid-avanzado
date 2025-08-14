"""
🏢 PISO 3 - OFICINA IA
FVG ML Predictor - Sistema de Machine Learning para predicción de FVGs
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import logging
import sqlite3
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import joblib

# Configurar rutas
current_dir = Path(__file__).parent
project_root = current_dir.parents[3]
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src" / "core"))

# Imports ML
try:
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
    import pickle
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

# Imports centralizados
from data_manager import DataManager
from logger_manager import LoggerManager

class FVGPrediction(Enum):
    """Tipos de predicción para FVGs"""
    FILL_HIGH = "FILL_HIGH"      # Alta probabilidad de llenado
    FILL_MEDIUM = "FILL_MEDIUM"  # Probabilidad media de llenado
    FILL_LOW = "FILL_LOW"        # Baja probabilidad de llenado
    NO_FILL = "NO_FILL"          # Muy baja probabilidad de llenado

@dataclass
class FVGMLResult:
    """Resultado de predicción ML"""
    fvg_id: str
    prediction: FVGPrediction
    probability: float
    confidence: float
    features_used: Dict[str, float]
    model_version: str

class FVGMLPredictor:
    """
    Predictor de Machine Learning para FVGs
    
    CARACTERÍSTICAS DEL MODELO:
    1. Predice probabilidad de llenado de FVGs
    2. Usa múltiples timeframes
    3. Incluye contexto de mercado
    4. Entrenamiento continuo
    5. Validación cruzada
    """
    
    def __init__(self, db_path: Optional[str] = None):
        self.logger = LoggerManager().get_logger("FVGMLPredictor")
        self.data_manager = DataManager()
        
        # Rutas de modelos
        self.models_dir = project_root / "data" / "ml" / "models"
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Base de datos
        self.db_path = db_path or str(project_root / "data" / "ml" / "fvg_master.db")
        
        # Modelos ML
        self.model = None
        self.scaler = None
        self.label_encoder = None
        self.model_version = "1.0.0"
        self.is_trained = False
        
        # Configuración de features
        self.feature_columns = [
            'fvg_size_pips', 'fvg_duration_minutes', 'distance_to_price',
            'market_volatility', 'trend_strength', 'volume_factor',
            'session_factor', 'confluence_score', 'atr_ratio',
            'rsi_value', 'bb_position', 'ema_alignment'
        ]
        
        # Verificar disponibilidad ML
        if not ML_AVAILABLE:
            self.logger.warning("Scikit-learn no disponible. Funcionalidad ML limitada.")
        
        self.logger.info("FVGMLPredictor inicializado")

    def prepare_training_data(self, symbol: str = "EURUSD", days_back: int = 30) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prepara datos de entrenamiento desde la base de datos
        
        Args:
            symbol: Símbolo del instrumento
            days_back: Días hacia atrás para obtener datos
            
        Returns:
            Tuple de (features_df, target_series)
        """
        try:
            if not ML_AVAILABLE:
                self.logger.error("Scikit-learn no disponible para entrenamiento")
                return pd.DataFrame(), pd.Series()
            
            # Conectar a base de datos
            conn = sqlite3.connect(self.db_path)
            
            # Obtener FVGs históricos con resultado conocido
            cutoff_date = datetime.now() - timedelta(days=days_back)
            
            query = """
            SELECT * FROM fvg_detections 
            WHERE symbol = ? 
            AND detection_time > ? 
            AND filled_status IS NOT NULL
            ORDER BY detection_time
            """
            
            df_fvgs = pd.read_sql_query(query, conn, params=[symbol, cutoff_date])
            conn.close()
            
            if len(df_fvgs) == 0:
                self.logger.warning("No hay datos históricos suficientes para entrenamiento")
                return pd.DataFrame(), pd.Series()
            
            # Preparar features para cada FVG
            features_list = []
            targets_list = []
            
            for _, fvg_row in df_fvgs.iterrows():
                try:
                    # Extraer features del FVG
                    features = self._extract_features_for_fvg(fvg_row, symbol)
                    if features is not None:
                        features_list.append(features)
                        
                        # Target: si el FVG fue llenado
                        target = 1 if fvg_row['filled_status'] == 'FILLED' else 0
                        targets_list.append(target)
                        
                except Exception as e:
                    self.logger.error(f"Error procesando FVG {fvg_row.get('id', 'unknown')}: {e}")
                    continue
            
            if len(features_list) == 0:
                self.logger.warning("No se pudieron extraer features válidas")
                return pd.DataFrame(), pd.Series()
            
            # Convertir a DataFrames
            features_df = pd.DataFrame(features_list)
            target_series = pd.Series(targets_list)
            
            self.logger.info(f"Datos de entrenamiento preparados: {len(features_df)} muestras")
            
            return features_df, target_series
            
        except Exception as e:
            self.logger.error(f"Error preparando datos de entrenamiento: {e}")
            return pd.DataFrame(), pd.Series()

    def _extract_features_for_fvg(self, fvg_row: pd.Series, symbol: str) -> Optional[Dict[str, float]]:
        """Extrae features para un FVG específico"""
        try:
            # Tiempo del FVG
            fvg_time = pd.to_datetime(fvg_row['detection_time'])
            
            # Obtener datos de mercado en el momento del FVG
            df_h1 = self.data_manager.get_ohlc_data(symbol, 'H1', 50, end_time=fvg_time)
            df_m15 = self.data_manager.get_ohlc_data(symbol, 'M15', 100, end_time=fvg_time)
            
            if df_h1 is None or df_m15 is None or len(df_h1) < 20 or len(df_m15) < 50:
                return None
            
            # Features básicas del FVG
            fvg_high = fvg_row['high_price']
            fvg_low = fvg_row['low_price']
            fvg_size = fvg_high - fvg_low
            
            # 1. Tamaño del FVG en pips
            fvg_size_pips = fvg_size * 10000  # Para EURUSD
            
            # 2. Duración de formación
            start_time = pd.to_datetime(fvg_row.get('start_time', fvg_time))
            end_time = pd.to_datetime(fvg_row.get('end_time', fvg_time))
            fvg_duration_minutes = (end_time - start_time).total_seconds() / 60
            
            # 3. Distancia al precio actual
            current_price = df_m15['close'].iloc[-1]
            fvg_center = (fvg_high + fvg_low) / 2
            distance_to_price = abs(current_price - fvg_center) * 10000
            
            # 4. Volatilidad del mercado (ATR)
            atr_h1 = self._calculate_atr(df_h1, 14)
            market_volatility = atr_h1.iloc[-1] * 10000
            
            # 5. Fuerza de tendencia (EMAs)
            ema_20 = df_h1['close'].ewm(span=20).mean().iloc[-1]
            ema_50 = df_h1['close'].ewm(span=50).mean().iloc[-1]
            trend_strength = abs(ema_20 - ema_50) / ema_50
            
            # 6. Factor de volumen
            volume_factor = self._calculate_volume_factor(df_m15)
            
            # 7. Factor de sesión
            session_factor = self._calculate_session_factor(fvg_time)
            
            # 8. Score de confluencia
            confluence_score = self._calculate_confluence_score(df_h1, fvg_center)
            
            # 9. Ratio ATR
            atr_ratio = fvg_size / atr_h1.iloc[-1] if atr_h1.iloc[-1] > 0 else 0
            
            # 10. RSI
            rsi_value = self._calculate_rsi(df_h1['close'], 14).iloc[-1]
            
            # 11. Posición en Bandas de Bollinger
            bb_position = self._calculate_bb_position(df_h1)
            
            # 12. Alineación de EMAs
            ema_alignment = self._calculate_ema_alignment(df_h1)
            
            features = {
                'fvg_size_pips': fvg_size_pips,
                'fvg_duration_minutes': fvg_duration_minutes,
                'distance_to_price': distance_to_price,
                'market_volatility': market_volatility,
                'trend_strength': trend_strength,
                'volume_factor': volume_factor,
                'session_factor': session_factor,
                'confluence_score': confluence_score,
                'atr_ratio': atr_ratio,
                'rsi_value': rsi_value,
                'bb_position': bb_position,
                'ema_alignment': ema_alignment
            }
            
            return features
            
        except Exception as e:
            self.logger.error(f"Error extrayendo features: {e}")
            return None

    def train_model(self, symbol: str = "EURUSD", days_back: int = 30) -> bool:
        """
        Entrena el modelo ML con datos históricos
        
        Args:
            symbol: Símbolo del instrumento
            days_back: Días hacia atrás para entrenamiento
            
        Returns:
            True si el entrenamiento fue exitoso
        """
        try:
            if not ML_AVAILABLE:
                self.logger.error("Scikit-learn no disponible para entrenamiento")
                return False
            
            # Preparar datos
            X, y = self.prepare_training_data(symbol, days_back)
            
            if len(X) == 0 or len(y) == 0:
                self.logger.error("No hay datos suficientes para entrenamiento")
                return False
            
            # Verificar balance de clases
            class_counts = y.value_counts()
            self.logger.info(f"Balance de clases: {dict(class_counts)}")
            
            if len(class_counts) < 2:
                self.logger.error("No hay suficiente variedad en las clases target")
                return False
            
            # Dividir datos
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Escalar features
            self.scaler = StandardScaler()
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Entrenar modelo ensemble
            self.model = GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=6,
                random_state=42
            )
            
            self.model.fit(X_train_scaled, y_train)
            
            # Evaluar modelo
            y_pred = self.model.predict(X_test_scaled)
            accuracy = accuracy_score(y_test, y_pred)
            
            # Validación cruzada
            cv_scores = cross_val_score(self.model, X_train_scaled, y_train, cv=5)
            cv_mean = cv_scores.mean()
            cv_std = cv_scores.std()
            
            self.logger.info(f"Accuracy en test: {accuracy:.3f}")
            self.logger.info(f"CV Score: {cv_mean:.3f} (+/- {cv_std * 2:.3f})")
            
            # Importancia de features
            feature_importance = dict(zip(X.columns, self.model.feature_importances_))
            sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
            
            self.logger.info("Top 5 features más importantes:")
            for feature, importance in sorted_features[:5]:
                self.logger.info(f"  {feature}: {importance:.3f}")
            
            # Guardar modelo
            self._save_model()
            
            self.is_trained = True
            self.logger.info("Modelo entrenado exitosamente")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error entrenando modelo: {e}")
            return False

    def predict_fvg_fill(self, fvg_data: Dict, symbol: str = "EURUSD") -> FVGMLResult:
        """
        Predice la probabilidad de llenado de un FVG
        
        Args:
            fvg_data: Datos del FVG a predecir
            symbol: Símbolo del instrumento
            
        Returns:
            FVGMLResult con la predicción
        """
        try:
            if not ML_AVAILABLE or not self.is_trained:
                # Fallback: predicción simple basada en reglas
                return self._fallback_prediction(fvg_data, symbol)
            
            # Extraer features del FVG actual
            features = self._extract_current_features(fvg_data, symbol)
            if features is None:
                return self._fallback_prediction(fvg_data, symbol)
            
            # Preparar para predicción
            features_df = pd.DataFrame([features])
            features_scaled = self.scaler.transform(features_df)
            
            # Predicción
            probability = self.model.predict_proba(features_scaled)[0][1]  # Probabilidad de clase 1 (FILLED)
            
            # Determinar categoría de predicción
            if probability >= 0.75:
                prediction = FVGPrediction.FILL_HIGH
            elif probability >= 0.50:
                prediction = FVGPrediction.FILL_MEDIUM
            elif probability >= 0.25:
                prediction = FVGPrediction.FILL_LOW
            else:
                prediction = FVGPrediction.NO_FILL
            
            # Calcular confianza basada en la distancia a 0.5
            confidence = abs(probability - 0.5) * 2
            
            result = FVGMLResult(
                fvg_id=fvg_data.get('id', 'unknown'),
                prediction=prediction,
                probability=probability,
                confidence=confidence,
                features_used=features,
                model_version=self.model_version
            )
            
            self.logger.info(f"Predicción FVG {result.fvg_id}: {prediction.value} (prob={probability:.3f})")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error en predicción ML: {e}")
            return self._fallback_prediction(fvg_data, symbol)

    def _extract_current_features(self, fvg_data: Dict, symbol: str) -> Optional[Dict[str, float]]:
        """Extrae features del FVG actual para predicción"""
        try:
            # Obtener datos de mercado actuales
            df_h1 = self.data_manager.get_ohlc_data(symbol, 'H1', 50)
            df_m15 = self.data_manager.get_ohlc_data(symbol, 'M15', 100)
            
            if df_h1 is None or df_m15 is None:
                return None
            
            # Extraer features igual que en entrenamiento
            fvg_high = fvg_data.get('high', 0)
            fvg_low = fvg_data.get('low', 0)
            fvg_size = fvg_high - fvg_low
            
            # Calcular todas las features
            features = {
                'fvg_size_pips': fvg_size * 10000,
                'fvg_duration_minutes': 5.0,  # Asumido
                'distance_to_price': abs(df_m15['close'].iloc[-1] - (fvg_high + fvg_low) / 2) * 10000,
                'market_volatility': self._calculate_atr(df_h1, 14).iloc[-1] * 10000,
                'trend_strength': self._calculate_trend_strength(df_h1),
                'volume_factor': self._calculate_volume_factor(df_m15),
                'session_factor': self._calculate_session_factor(datetime.now()),
                'confluence_score': self._calculate_confluence_score(df_h1, (fvg_high + fvg_low) / 2),
                'atr_ratio': fvg_size / self._calculate_atr(df_h1, 14).iloc[-1],
                'rsi_value': self._calculate_rsi(df_h1['close'], 14).iloc[-1],
                'bb_position': self._calculate_bb_position(df_h1),
                'ema_alignment': self._calculate_ema_alignment(df_h1)
            }
            
            return features
            
        except Exception as e:
            self.logger.error(f"Error extrayendo features actuales: {e}")
            return None

    def _fallback_prediction(self, fvg_data: Dict, symbol: str) -> FVGMLResult:
        """Predicción de fallback cuando ML no está disponible"""
        try:
            # Predicción simple basada en reglas
            fvg_size = abs(fvg_data.get('high', 0) - fvg_data.get('low', 0))
            
            # Obtener ATR para normalizar
            df_h1 = self.data_manager.get_ohlc_data(symbol, 'H1', 24)
            if df_h1 is not None:
                atr = self._calculate_atr(df_h1, 14).iloc[-1]
                size_ratio = fvg_size / atr if atr > 0 else 1
            else:
                size_ratio = 1
            
            # Regla simple: FVGs más pequeños tienen mayor probabilidad de llenado
            if size_ratio < 0.5:
                probability = 0.8
                prediction = FVGPrediction.FILL_HIGH
            elif size_ratio < 1.0:
                probability = 0.6
                prediction = FVGPrediction.FILL_MEDIUM
            elif size_ratio < 2.0:
                probability = 0.4
                prediction = FVGPrediction.FILL_LOW
            else:
                probability = 0.2
                prediction = FVGPrediction.NO_FILL
            
            return FVGMLResult(
                fvg_id=fvg_data.get('id', 'fallback'),
                prediction=prediction,
                probability=probability,
                confidence=0.5,
                features_used={'size_ratio': size_ratio},
                model_version="fallback"
            )
            
        except Exception as e:
            self.logger.error(f"Error en predicción fallback: {e}")
            return FVGMLResult(
                fvg_id=fvg_data.get('id', 'error'),
                prediction=FVGPrediction.NO_FILL,
                probability=0.0,
                confidence=0.0,
                features_used={},
                model_version="error"
            )

    def _save_model(self):
        """Guarda el modelo entrenado"""
        try:
            model_path = self.models_dir / f"fvg_ml_model_{self.model_version}.pkl"
            scaler_path = self.models_dir / f"fvg_scaler_{self.model_version}.pkl"
            
            joblib.dump(self.model, model_path)
            joblib.dump(self.scaler, scaler_path)
            
            self.logger.info(f"Modelo guardado en {model_path}")
            
        except Exception as e:
            self.logger.error(f"Error guardando modelo: {e}")

    def load_model(self, version: str = None):
        """Carga un modelo guardado"""
        try:
            version = version or self.model_version
            model_path = self.models_dir / f"fvg_ml_model_{version}.pkl"
            scaler_path = self.models_dir / f"fvg_scaler_{version}.pkl"
            
            if model_path.exists() and scaler_path.exists():
                self.model = joblib.load(model_path)
                self.scaler = joblib.load(scaler_path)
                self.is_trained = True
                self.model_version = version
                
                self.logger.info(f"Modelo {version} cargado exitosamente")
                return True
            else:
                self.logger.warning(f"Modelo {version} no encontrado")
                return False
                
        except Exception as e:
            self.logger.error(f"Error cargando modelo: {e}")
            return False

    # Métodos auxiliares para cálculos técnicos
    def _calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calcula Average True Range"""
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        
        true_range = np.maximum(high_low, np.maximum(high_close, low_close))
        return true_range.rolling(window=period).mean()

    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calcula RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def _calculate_trend_strength(self, df: pd.DataFrame) -> float:
        """Calcula fuerza de tendencia"""
        try:
            ema_20 = df['close'].ewm(span=20).mean().iloc[-1]
            ema_50 = df['close'].ewm(span=50).mean().iloc[-1]
            return abs(ema_20 - ema_50) / ema_50
        except:
            return 0.0

    def _calculate_volume_factor(self, df: pd.DataFrame) -> float:
        """Calcula factor de volumen"""
        try:
            if 'volume' in df.columns:
                return df['volume'].tail(10).mean() / df['volume'].mean()
            return 1.0
        except:
            return 1.0

    def _calculate_session_factor(self, timestamp: datetime) -> float:
        """Calcula factor de sesión"""
        try:
            hour = timestamp.hour
            if 8 <= hour <= 16:  # London + NY
                return 1.0
            elif 0 <= hour <= 8:  # Tokyo
                return 0.7
            else:
                return 0.5
        except:
            return 0.5

    def _calculate_confluence_score(self, df: pd.DataFrame, level: float) -> float:
        """Calcula score de confluencia"""
        try:
            # Simplificado para el ejemplo
            ema_20 = df['close'].ewm(span=20).mean().iloc[-1]
            distance = abs(level - ema_20) / ema_20
            return max(0, 1 - distance * 10)
        except:
            return 0.5

    def _calculate_bb_position(self, df: pd.DataFrame) -> float:
        """Calcula posición en Bandas de Bollinger"""
        try:
            sma = df['close'].rolling(20).mean()
            std = df['close'].rolling(20).std()
            upper = sma + 2 * std
            lower = sma - 2 * std
            current = df['close'].iloc[-1]
            
            return (current - lower.iloc[-1]) / (upper.iloc[-1] - lower.iloc[-1])
        except:
            return 0.5

    def _calculate_ema_alignment(self, df: pd.DataFrame) -> float:
        """Calcula alineación de EMAs"""
        try:
            ema_10 = df['close'].ewm(span=10).mean().iloc[-1]
            ema_20 = df['close'].ewm(span=20).mean().iloc[-1]
            ema_50 = df['close'].ewm(span=50).mean().iloc[-1]
            
            if ema_10 > ema_20 > ema_50:
                return 1.0  # Alcista
            elif ema_10 < ema_20 < ema_50:
                return -1.0  # Bajista
            else:
                return 0.0  # Neutral
        except:
            return 0.0

    def get_model_performance(self) -> Dict:
        """Obtiene métricas de rendimiento del modelo"""
        if not self.is_trained:
            return {"error": "Modelo no entrenado"}
        
        try:
            # Obtener datos recientes para evaluación
            X, y = self.prepare_training_data(days_back=7)
            if len(X) == 0:
                return {"error": "No hay datos para evaluación"}
            
            X_scaled = self.scaler.transform(X)
            y_pred = self.model.predict(X_scaled)
            y_prob = self.model.predict_proba(X_scaled)[:, 1]
            
            accuracy = accuracy_score(y, y_pred)
            
            return {
                "accuracy": accuracy,
                "total_predictions": len(y),
                "positive_predictions": sum(y_pred),
                "average_probability": np.mean(y_prob),
                "model_version": self.model_version
            }
            
        except Exception as e:
            return {"error": str(e)}


if __name__ == "__main__":
    # Test básico del predictor ML
    predictor = FVGMLPredictor()
    
    # Cargar modelo si existe
    if not predictor.load_model():
        print("Entrenando nuevo modelo...")
        success = predictor.train_model(days_back=30)
        if not success:
            print("❌ Error en entrenamiento")
        else:
            print("✅ Modelo entrenado exitosamente")
    
    # Test de predicción
    test_fvg = {
        'id': 'test_ml_001',
        'type': 'BULLISH',
        'high': 1.0950,
        'low': 1.0930
    }
    
    result = predictor.predict_fvg_fill(test_fvg)
    
    print(f"\n🏢 PISO 3 - OFICINA IA")
    print(f"FVG ID: {result.fvg_id}")
    print(f"Predicción: {result.prediction.value}")
    print(f"Probabilidad: {result.probability:.3f}")
    print(f"Confianza: {result.confidence:.3f}")
    print(f"Modelo: {result.model_version}")
    
    # Mostrar rendimiento
    performance = predictor.get_model_performance()
    print(f"\nRendimiento del modelo: {performance}")
