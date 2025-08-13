# 🗄️ DISEÑO BASE DE DATOS FVG OPTIMIZADA PARA ML

## 📊 **ESTRUCTURA DE TABLAS PRINCIPALES**

### **1. 🎯 TABLA CORE: `fvg_master`**
```sql
CREATE TABLE fvg_master (
    -- Identificación única
    fvg_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    timestamp_creation DATETIME,
    symbol VARCHAR(10),
    timeframe VARCHAR(5),
    
    -- Datos OHLC de formación (3 velas)
    vela1_open DECIMAL(10,5),
    vela1_high DECIMAL(10,5), 
    vela1_low DECIMAL(10,5),
    vela1_close DECIMAL(10,5),
    vela1_volume BIGINT,
    
    vela2_open DECIMAL(10,5),
    vela2_high DECIMAL(10,5),
    vela2_low DECIMAL(10,5), 
    vela2_close DECIMAL(10,5),
    vela2_volume BIGINT,
    
    vela3_open DECIMAL(10,5),
    vela3_high DECIMAL(10,5),
    vela3_low DECIMAL(10,5),
    vela3_close DECIMAL(10,5),
    vela3_volume BIGINT,
    
    -- Características del FVG
    gap_high DECIMAL(10,5),
    gap_low DECIMAL(10,5),
    gap_size_pips DECIMAL(6,2),
    gap_type ENUM('BULLISH', 'BEARISH'),
    
    -- Estado y resultados
    status ENUM('PENDING', 'FILLED', 'PARTIALLY_FILLED', 'EXPIRED'),
    fill_timestamp DATETIME,
    fill_percentage DECIMAL(5,2),
    time_to_fill_hours DECIMAL(8,2),
    
    -- Índices para ML
    quality_score DECIMAL(4,2),
    ml_features_calculated BOOLEAN DEFAULT FALSE,
    
    INDEX idx_symbol_timeframe (symbol, timeframe),
    INDEX idx_timestamp (timestamp_creation),
    INDEX idx_status (status),
    INDEX idx_quality (quality_score)
);
```

### **2. 🧮 TABLA ML: `fvg_features`**
```sql
CREATE TABLE fvg_features (
    fvg_id BIGINT PRIMARY KEY,
    
    -- Features técnicos básicos
    atr_20 DECIMAL(8,5),
    rsi_14 DECIMAL(5,2),
    bb_position DECIMAL(5,2),
    volume_ratio DECIMAL(6,2),
    
    -- Features de contexto
    trend_direction ENUM('UP', 'DOWN', 'SIDEWAYS'),
    trend_strength DECIMAL(5,2),
    market_session ENUM('ASIA', 'LONDON', 'NY', 'OVERLAP'),
    
    -- Features de estructura
    near_support_resistance BOOLEAN,
    distance_to_sr DECIMAL(6,2),
    confluence_count INT,
    
    -- Features temporales
    hour_of_day INT,
    day_of_week INT,
    is_news_time BOOLEAN,
    
    -- Features de volatilidad
    volatility_percentile DECIMAL(5,2),
    volume_percentile DECIMAL(5,2),
    
    -- Features avanzados
    fractal_dimension DECIMAL(6,4),
    hurst_exponent DECIMAL(6,4),
    entropy_measure DECIMAL(6,4),
    
    FOREIGN KEY (fvg_id) REFERENCES fvg_master(fvg_id)
);
```

### **3. 📈 TABLA PREDICCIONES: `fvg_predictions`**
```sql
CREATE TABLE fvg_predictions (
    prediction_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    fvg_id BIGINT,
    model_name VARCHAR(50),
    model_version VARCHAR(20),
    
    -- Predicciones
    predicted_fill_probability DECIMAL(5,2),
    predicted_time_to_fill DECIMAL(8,2),
    predicted_quality_score DECIMAL(4,2),
    confidence_level DECIMAL(5,2),
    
    -- Validación
    actual_filled BOOLEAN,
    actual_time_to_fill DECIMAL(8,2),
    prediction_accuracy DECIMAL(5,2),
    
    timestamp_prediction DATETIME,
    
    FOREIGN KEY (fvg_id) REFERENCES fvg_master(fvg_id),
    INDEX idx_model (model_name, model_version),
    INDEX idx_accuracy (prediction_accuracy)
);
```

### **4. 🔄 TABLA TIEMPO REAL: `fvg_live_status`**
```sql
CREATE TABLE fvg_live_status (
    fvg_id BIGINT PRIMARY KEY,
    
    -- Estado actual
    current_price DECIMAL(10,5),
    distance_to_gap DECIMAL(6,2),
    partial_fill_percentage DECIMAL(5,2),
    
    -- Monitoreo tiempo real
    last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    alert_triggered BOOLEAN DEFAULT FALSE,
    signal_generated BOOLEAN DEFAULT FALSE,
    
    -- Trading
    position_opened BOOLEAN DEFAULT FALSE,
    position_id VARCHAR(50),
    entry_price DECIMAL(10,5),
    current_pnl DECIMAL(10,2),
    
    FOREIGN KEY (fvg_id) REFERENCES fvg_master(fvg_id)
);
```

## 🚀 **OPTIMIZACIONES PARA ML**

### **📊 VISTAS MATERIALIZADAS**
```sql
-- Vista para entrenamiento ML
CREATE VIEW ml_training_dataset AS
SELECT 
    fm.*,
    ff.*,
    fp.predicted_fill_probability,
    (fm.status = 'FILLED') AS target_filled,
    CASE 
        WHEN fm.time_to_fill_hours < 4 THEN 'FAST'
        WHEN fm.time_to_fill_hours < 24 THEN 'MEDIUM'
        ELSE 'SLOW'
    END AS target_speed_category
FROM fvg_master fm
JOIN fvg_features ff ON fm.fvg_id = ff.fvg_id
LEFT JOIN fvg_predictions fp ON fm.fvg_id = fp.fvg_id
WHERE fm.ml_features_calculated = TRUE;

-- Vista para análisis de performance
CREATE VIEW model_performance_summary AS
SELECT 
    model_name,
    model_version,
    COUNT(*) as total_predictions,
    AVG(prediction_accuracy) as avg_accuracy,
    STDDEV(prediction_accuracy) as accuracy_std,
    COUNT(CASE WHEN prediction_accuracy > 0.8 THEN 1 END) as high_accuracy_count
FROM fvg_predictions
GROUP BY model_name, model_version;
```

### **⚡ ÍNDICES OPTIMIZADOS**
```sql
-- Índices compuestos para consultas ML frecuentes
CREATE INDEX idx_ml_features_combo ON fvg_features 
(market_session, trend_direction, quality_score);

CREATE INDEX idx_temporal_analysis ON fvg_master 
(symbol, timeframe, timestamp_creation);

CREATE INDEX idx_performance_tracking ON fvg_predictions 
(model_name, timestamp_prediction, prediction_accuracy);
```

## 📦 **PROCEDIMIENTOS ALMACENADOS ML**

### **🔄 ACTUALIZACIÓN AUTOMÁTICA**
```sql
DELIMITER //
CREATE PROCEDURE UpdateFVGStatus()
BEGIN
    -- Actualizar FVGs que han sido llenados
    UPDATE fvg_master fm
    JOIN fvg_live_status fls ON fm.fvg_id = fls.fvg_id
    SET fm.status = 'FILLED',
        fm.fill_timestamp = NOW(),
        fm.time_to_fill_hours = TIMESTAMPDIFF(HOUR, fm.timestamp_creation, NOW())
    WHERE fm.status = 'PENDING' 
    AND fls.partial_fill_percentage >= 100;
    
    -- Actualizar predicciones con resultados reales
    UPDATE fvg_predictions fp
    JOIN fvg_master fm ON fp.fvg_id = fm.fvg_id
    SET fp.actual_filled = (fm.status = 'FILLED'),
        fp.actual_time_to_fill = fm.time_to_fill_hours,
        fp.prediction_accuracy = CASE 
            WHEN fp.predicted_fill_probability > 0.5 AND fm.status = 'FILLED' THEN 1.0
            WHEN fp.predicted_fill_probability <= 0.5 AND fm.status != 'FILLED' THEN 1.0
            ELSE 0.0
        END
    WHERE fp.actual_filled IS NULL AND fm.status IN ('FILLED', 'EXPIRED');
END //
DELIMITER ;
```

## 🎯 **CONFIGURACIÓN DE ALMACENAMIENTO**

### **💾 ESTRATEGIA DE PARTICIONADO**
```sql
-- Particionar por fecha para optimizar consultas temporales
ALTER TABLE fvg_master 
PARTITION BY RANGE (YEAR(timestamp_creation)) (
    PARTITION p2023 VALUES LESS THAN (2024),
    PARTITION p2024 VALUES LESS THAN (2025),
    PARTITION p2025 VALUES LESS THAN (2026),
    PARTITION p_future VALUES LESS THAN MAXVALUE
);
```

### **🔧 CONFIGURACIÓN MYSQL OPTIMIZADA**
```ini
[mysqld]
# Optimizaciones para ML
innodb_buffer_pool_size = 2G
innodb_log_file_size = 512M
innodb_flush_log_at_trx_commit = 2
query_cache_size = 256M
key_buffer_size = 512M

# Configuraciones específicas para FVG ML
max_connections = 200
innodb_thread_concurrency = 16
tmp_table_size = 256M
max_heap_table_size = 256M
```

## 📊 **MÉTRICAS DE PERFORMANCE**

### **🎯 KPIs DE LA BASE DE DATOS**
- **Velocidad inserción:** < 1ms por FVG
- **Consultas ML:** < 100ms para 10K registros  
- **Precisión modelos:** > 75% accuracy
- **Latencia tiempo real:** < 50ms updates
- **Almacenamiento:** ~500MB por millón FVGs

---

**🎯 Esta estructura está optimizada para soportar 1M+ FVGs con consultas ML sub-segundo y entrenamiento eficiente de modelos.**
