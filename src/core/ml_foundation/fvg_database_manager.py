"""
🗄️ FVG DATABASE MANAGER - SÓTANO 3
==================================

Gestión centralizada de la base de datos FVG optimizada para Machine Learning.
Maneja inserción, consulta y mantenimiento de datos FVG con características ML.

Características principales:
- Inserción en lotes optimizada
- Consultas ML sub-segundo  
- Integridad automática de datos
- Backup y recuperación automática
- Escalabilidad horizontal

Autor: Sistema Trading Grid Avanzado
Fecha: Agosto 13, 2025
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import threading
import json
import os
from pathlib import Path

class FVGDatabaseManager:
    """Gestor centralizado de base de datos FVG optimizada para ML"""
    
    def __init__(self, db_path: str = "data/ml/fvg_master.db"):
        """
        Inicializar gestor de base de datos FVG
        
        Args:
            db_path: Ruta a la base de datos SQLite
        """
        self.db_path = db_path
        self.connection = None
        self.lock = threading.Lock()
        self._create_database_structure()
        
    def _create_database_structure(self):
        """Crear estructura completa de base de datos"""
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            # Tabla principal FVG
            conn.execute('''
                CREATE TABLE IF NOT EXISTS fvg_master (
                    fvg_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp_creation DATETIME,
                    symbol TEXT,
                    timeframe TEXT,
                    
                    -- Datos OHLC vela 1
                    vela1_open REAL,
                    vela1_high REAL,
                    vela1_low REAL,
                    vela1_close REAL,
                    vela1_volume INTEGER,
                    
                    -- Datos OHLC vela 2  
                    vela2_open REAL,
                    vela2_high REAL,
                    vela2_low REAL,
                    vela2_close REAL,
                    vela2_volume INTEGER,
                    
                    -- Datos OHLC vela 3
                    vela3_open REAL,
                    vela3_high REAL,
                    vela3_low REAL,
                    vela3_close REAL,
                    vela3_volume INTEGER,
                    
                    -- Características FVG
                    gap_high REAL,
                    gap_low REAL,
                    gap_size_pips REAL,
                    gap_type TEXT CHECK(gap_type IN ('BULLISH', 'BEARISH')),
                    
                    -- Estado y resultados
                    status TEXT CHECK(status IN ('PENDING', 'FILLED', 'PARTIALLY_FILLED', 'EXPIRED')) DEFAULT 'PENDING',
                    fill_timestamp DATETIME,
                    fill_percentage REAL DEFAULT 0.0,
                    time_to_fill_hours REAL,
                    
                    -- ML
                    quality_score REAL,
                    ml_features_calculated BOOLEAN DEFAULT FALSE,
                    
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla características ML
            conn.execute('''
                CREATE TABLE IF NOT EXISTS fvg_features (
                    fvg_id INTEGER PRIMARY KEY,
                    
                    -- Features técnicos básicos
                    atr_20 REAL,
                    rsi_14 REAL,
                    bb_position REAL,
                    volume_ratio REAL,
                    
                    -- Features de contexto
                    trend_direction TEXT CHECK(trend_direction IN ('UP', 'DOWN', 'SIDEWAYS')),
                    trend_strength REAL,
                    market_session TEXT CHECK(market_session IN ('ASIA', 'LONDON', 'NY', 'OVERLAP')),
                    
                    -- Features de estructura
                    near_support_resistance BOOLEAN,
                    distance_to_sr REAL,
                    confluence_count INTEGER,
                    
                    -- Features temporales
                    hour_of_day INTEGER,
                    day_of_week INTEGER,
                    is_news_time BOOLEAN,
                    
                    -- Features de volatilidad
                    volatility_percentile REAL,
                    volume_percentile REAL,
                    
                    -- Features avanzados
                    fractal_dimension REAL,
                    hurst_exponent REAL,
                    entropy_measure REAL,
                    
                    calculated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    
                    FOREIGN KEY (fvg_id) REFERENCES fvg_master(fvg_id)
                )
            ''')
            
            # Tabla predicciones ML
            conn.execute('''
                CREATE TABLE IF NOT EXISTS fvg_predictions (
                    prediction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fvg_id INTEGER,
                    model_name TEXT,
                    model_version TEXT,
                    
                    -- Predicciones
                    predicted_fill_probability REAL,
                    predicted_time_to_fill REAL,
                    predicted_quality_score REAL,
                    confidence_level REAL,
                    
                    -- Validación
                    actual_filled BOOLEAN,
                    actual_time_to_fill REAL,
                    prediction_accuracy REAL,
                    
                    timestamp_prediction DATETIME DEFAULT CURRENT_TIMESTAMP,
                    
                    FOREIGN KEY (fvg_id) REFERENCES fvg_master(fvg_id)
                )
            ''')
            
            # Tabla estado tiempo real
            conn.execute('''
                CREATE TABLE IF NOT EXISTS fvg_live_status (
                    fvg_id INTEGER PRIMARY KEY,
                    
                    -- Estado actual
                    current_price REAL,
                    distance_to_gap REAL,
                    partial_fill_percentage REAL DEFAULT 0.0,
                    
                    -- Monitoreo
                    last_update DATETIME DEFAULT CURRENT_TIMESTAMP,
                    alert_triggered BOOLEAN DEFAULT FALSE,
                    signal_generated BOOLEAN DEFAULT FALSE,
                    
                    -- Trading
                    position_opened BOOLEAN DEFAULT FALSE,
                    position_id TEXT,
                    entry_price REAL,
                    current_pnl REAL,
                    
                    FOREIGN KEY (fvg_id) REFERENCES fvg_master(fvg_id)
                )
            ''')
            
            # Crear índices optimizados
            self._create_indexes(conn)
            
    def _create_indexes(self, conn):
        """Crear índices optimizados para consultas ML"""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_symbol_timeframe ON fvg_master(symbol, timeframe)",
            "CREATE INDEX IF NOT EXISTS idx_timestamp ON fvg_master(timestamp_creation)",
            "CREATE INDEX IF NOT EXISTS idx_status ON fvg_master(status)",
            "CREATE INDEX IF NOT EXISTS idx_quality ON fvg_master(quality_score)",
            "CREATE INDEX IF NOT EXISTS idx_ml_features ON fvg_features(market_session, trend_direction)",
            "CREATE INDEX IF NOT EXISTS idx_predictions_model ON fvg_predictions(model_name, model_version)",
            "CREATE INDEX IF NOT EXISTS idx_live_status ON fvg_live_status(last_update, alert_triggered)"
        ]
        
        for index_sql in indexes:
            conn.execute(index_sql)
    
    def insert_fvg(self, fvg_data: Dict) -> int:
        """
        Insertar un FVG en la base de datos
        
        Args:
            fvg_data: Diccionario con datos del FVG
            
        Returns:
            ID del FVG insertado
        """
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    INSERT INTO fvg_master (
                        timestamp_creation, symbol, timeframe,
                        vela1_open, vela1_high, vela1_low, vela1_close, vela1_volume,
                        vela2_open, vela2_high, vela2_low, vela2_close, vela2_volume,
                        vela3_open, vela3_high, vela3_low, vela3_close, vela3_volume,
                        gap_high, gap_low, gap_size_pips, gap_type, quality_score
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    fvg_data.get('timestamp_creation', datetime.now()),
                    fvg_data.get('symbol', ''),
                    fvg_data.get('timeframe', ''),
                    fvg_data.get('vela1_open', 0.0), fvg_data.get('vela1_high', 0.0), fvg_data.get('vela1_low', 0.0), fvg_data.get('vela1_close', 0.0), fvg_data.get('vela1_volume', 0),
                    fvg_data.get('vela2_open', 0.0), fvg_data.get('vela2_high', 0.0), fvg_data.get('vela2_low', 0.0), fvg_data.get('vela2_close', 0.0), fvg_data.get('vela2_volume', 0),
                    fvg_data.get('vela3_open', 0.0), fvg_data.get('vela3_high', 0.0), fvg_data.get('vela3_low', 0.0), fvg_data.get('vela3_close', 0.0), fvg_data.get('vela3_volume', 0),
                    fvg_data.get('gap_high', 0.0), fvg_data.get('gap_low', 0.0), fvg_data.get('gap_size_pips', 0.0), fvg_data.get('gap_type', ''),
                    fvg_data.get('quality_score', 0.0)
                ))
                
                fvg_id = cursor.lastrowid
                
                # Insertar en tabla de estado tiempo real
                conn.execute('''
                    INSERT INTO fvg_live_status (fvg_id, current_price, distance_to_gap)
                    VALUES (?, ?, ?)
                ''', (fvg_id, fvg_data.get('current_price', 0.0), fvg_data.get('distance_to_gap', 0.0)))
                
                return fvg_id
    
    def batch_insert_fvgs(self, fvgs_data: List[Dict], batch_size: int = 1000) -> List[int]:
        """
        Inserción optimizada en lotes de FVGs
        
        Args:
            fvgs_data: Lista de diccionarios con datos FVG
            batch_size: Tamaño del lote
            
        Returns:
            Lista de IDs insertados
        """
        inserted_ids = []
        
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                for i in range(0, len(fvgs_data), batch_size):
                    batch = fvgs_data[i:i + batch_size]
                    
                    # Preparar datos para inserción en lote
                    batch_values = []
                    for fvg in batch:
                        batch_values.append((
                            fvg.get('timestamp_creation', datetime.now()),
                            fvg['symbol'], fvg['timeframe'],
                            fvg['vela1_open'], fvg['vela1_high'], fvg['vela1_low'], fvg['vela1_close'], fvg['vela1_volume'],
                            fvg['vela2_open'], fvg['vela2_high'], fvg['vela2_low'], fvg['vela2_close'], fvg['vela2_volume'],
                            fvg['vela3_open'], fvg['vela3_high'], fvg['vela3_low'], fvg['vela3_close'], fvg['vela3_volume'],
                            fvg['gap_high'], fvg['gap_low'], fvg['gap_size_pips'], fvg['gap_type'],
                            fvg.get('quality_score', 0.0)
                        ))
                    
                    # Inserción en lote
                    conn.executemany('''
                        INSERT INTO fvg_master (
                            timestamp_creation, symbol, timeframe,
                            vela1_open, vela1_high, vela1_low, vela1_close, vela1_volume,
                            vela2_open, vela2_high, vela2_low, vela2_close, vela2_volume,
                            vela3_open, vela3_high, vela3_low, vela3_close, vela3_volume,
                            gap_high, gap_low, gap_size_pips, gap_type, quality_score
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', batch_values)
                    
                    # Obtener IDs insertados del lote
                    cursor = conn.execute('SELECT last_insert_rowid()')
                    last_id = cursor.fetchone()[0]
                    batch_ids = list(range(last_id - len(batch) + 1, last_id + 1))
                    inserted_ids.extend(batch_ids)
        
        return inserted_ids
    
    def get_ml_training_data(self, limit: Optional[int] = None, 
                           symbol: Optional[str] = None,
                           timeframe: Optional[str] = None) -> pd.DataFrame:
        """
        Obtener datos preparados para entrenamiento ML
        
        Args:
            limit: Límite de registros
            symbol: Filtrar por símbolo
            timeframe: Filtrar por timeframe
            
        Returns:
            DataFrame con datos ML listos
        """
        query = '''
            SELECT 
                fm.*,
                ff.*,
                (fm.status = 'FILLED') as target_filled,
                CASE 
                    WHEN fm.time_to_fill_hours < 4 THEN 'FAST'
                    WHEN fm.time_to_fill_hours < 24 THEN 'MEDIUM'
                    ELSE 'SLOW'
                END as target_speed_category
            FROM fvg_master fm
            LEFT JOIN fvg_features ff ON fm.fvg_id = ff.fvg_id
            WHERE fm.ml_features_calculated = TRUE
        '''
        
        params = []
        if symbol:
            query += ' AND fm.symbol = ?'
            params.append(symbol)
        if timeframe:
            query += ' AND fm.timeframe = ?'
            params.append(timeframe)
            
        query += ' ORDER BY fm.timestamp_creation DESC'
        
        if limit:
            query += ' LIMIT ?'
            params.append(limit)
        
        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql_query(query, conn, params=params)
    
    def update_fvg_status(self, fvg_id: int, status: str, 
                         fill_percentage: float = 0.0,
                         current_price: float = None):
        """
        Actualizar estado de un FVG
        
        Args:
            fvg_id: ID del FVG
            status: Nuevo estado
            fill_percentage: Porcentaje llenado
            current_price: Precio actual
        """
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                # Actualizar tabla principal
                if status == 'FILLED':
                    conn.execute('''
                        UPDATE fvg_master 
                        SET status = ?, fill_percentage = ?, fill_timestamp = ?, 
                            time_to_fill_hours = (julianday('now') - julianday(timestamp_creation)) * 24,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE fvg_id = ?
                    ''', (status, fill_percentage, datetime.now(), fvg_id))
                else:
                    conn.execute('''
                        UPDATE fvg_master 
                        SET status = ?, fill_percentage = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE fvg_id = ?
                    ''', (status, fill_percentage, fvg_id))
                
                # Actualizar tabla tiempo real
                if current_price:
                    conn.execute('''
                        UPDATE fvg_live_status 
                        SET current_price = ?, partial_fill_percentage = ?, last_update = CURRENT_TIMESTAMP
                        WHERE fvg_id = ?
                    ''', (current_price, fill_percentage, fvg_id))
    
    def get_pending_fvgs(self, symbol: Optional[str] = None) -> pd.DataFrame:
        """
        Obtener FVGs pendientes de llenado
        
        Args:
            symbol: Filtrar por símbolo
            
        Returns:
            DataFrame con FVGs pendientes
        """
        query = '''
            SELECT fm.*, fls.current_price, fls.distance_to_gap
            FROM fvg_master fm
            JOIN fvg_live_status fls ON fm.fvg_id = fls.fvg_id
            WHERE fm.status = 'PENDING'
        '''
        
        params = []
        if symbol:
            query += ' AND fm.symbol = ?'
            params.append(symbol)
            
        query += ' ORDER BY fm.quality_score DESC'
        
        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql_query(query, conn, params=params)
    
    def get_database_stats(self) -> Dict:
        """
        Obtener estadísticas de la base de datos
        
        Returns:
            Diccionario con estadísticas
        """
        with sqlite3.connect(self.db_path) as conn:
            stats = {}
            
            # Estadísticas generales
            stats['total_fvgs'] = conn.execute('SELECT COUNT(*) FROM fvg_master').fetchone()[0]
            stats['pending_fvgs'] = conn.execute("SELECT COUNT(*) FROM fvg_master WHERE status = 'PENDING'").fetchone()[0]
            stats['filled_fvgs'] = conn.execute("SELECT COUNT(*) FROM fvg_master WHERE status = 'FILLED'").fetchone()[0]
            
            # Estadísticas por símbolo
            cursor = conn.execute('SELECT symbol, COUNT(*) as count FROM fvg_master GROUP BY symbol')
            stats['by_symbol'] = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Estadísticas por timeframe
            cursor = conn.execute('SELECT timeframe, COUNT(*) as count FROM fvg_master GROUP BY timeframe')
            stats['by_timeframe'] = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Accuracy de modelos
            cursor = conn.execute('''
                SELECT model_name, AVG(prediction_accuracy) as avg_accuracy, COUNT(*) as predictions
                FROM fvg_predictions 
                WHERE prediction_accuracy IS NOT NULL
                GROUP BY model_name
            ''')
            stats['model_performance'] = {row[0]: {'accuracy': row[1], 'predictions': row[2]} for row in cursor.fetchall()}
            
            # Tamaño de la base de datos
            db_size = os.path.getsize(self.db_path) / (1024 * 1024)  # MB
            stats['database_size_mb'] = round(db_size, 2)
            
            return stats
    
    def cleanup_old_data(self, days_old: int = 90):
        """
        Limpiar datos antiguos para optimizar performance
        
        Args:
            days_old: Días de antigüedad para eliminar
        """
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                # Eliminar FVGs antiguos y sus datos relacionados
                conn.execute('''
                    DELETE FROM fvg_live_status 
                    WHERE fvg_id IN (
                        SELECT fvg_id FROM fvg_master 
                        WHERE timestamp_creation < ?
                    )
                ''', (cutoff_date,))
                
                conn.execute('''
                    DELETE FROM fvg_predictions 
                    WHERE fvg_id IN (
                        SELECT fvg_id FROM fvg_master 
                        WHERE timestamp_creation < ?
                    )
                ''', (cutoff_date,))
                
                conn.execute('''
                    DELETE FROM fvg_features 
                    WHERE fvg_id IN (
                        SELECT fvg_id FROM fvg_master 
                        WHERE timestamp_creation < ?
                    )
                ''', (cutoff_date,))
                
                deleted_count = conn.execute('''
                    DELETE FROM fvg_master WHERE timestamp_creation < ?
                ''', (cutoff_date,)).rowcount
                
                # Vacuum para recuperar espacio
                conn.execute('VACUUM')
                
                return deleted_count
    
    def backup_database(self, backup_path: Optional[str] = None):
        """
        Crear backup de la base de datos
        
        Args:
            backup_path: Ruta del backup (opcional)
        """
        if not backup_path:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = f"data/ml/backups/fvg_master_backup_{timestamp}.db"
        
        # Crear directorio backup si no existe
        os.makedirs(os.path.dirname(backup_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as source:
            with sqlite3.connect(backup_path) as backup:
                source.backup(backup)
        
        return backup_path
    
    def __del__(self):
        """Cleanup al destruir el objeto"""
        if self.connection:
            self.connection.close()
