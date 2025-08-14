"""
🌐 CONFIGURACIÓN DE FUENTES DE DATOS
==================================

Configuración centralizada para todas las fuentes de datos del sistema
Compatible con MT5, Alpha Vantage, Yahoo Finance y fuentes de backup

AUTOR: Trading Grid System
FECHA: 2025-08-13
VERSIÓN: 1.0.0
"""

import os
from typing import Dict, Optional, Any

class DataSourcesConfig:
    """Configuración centralizada de fuentes de datos"""
    
    def __init__(self):
        # 🔐 Configuración de MT5
        self.MT5_CONFIG = {
            'enabled': True,
            'login': int(os.getenv('MT5_LOGIN', '0')),
            'password': os.getenv('MT5_PASSWORD', ''),
            'server': os.getenv('MT5_SERVER', 'MetaQuotes-Demo'),
            'path': os.getenv('MT5_PATH', ''),
            'timeout': 60000,
            'retry_attempts': 3,
            'symbols': ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD'],
            'timeframes': {
                'M1': 1,
                'M5': 5,
                'M15': 15,
                'H1': 60,
                'H4': 240,
                'D1': 1440
            }
        }
        
        # 🔐 Configuración de Alpha Vantage
        self.ALPHA_VANTAGE_CONFIG = {
            'enabled': True,
            'api_key': os.getenv('ALPHA_VANTAGE_API_KEY', 'demo'),
            'base_url': 'https://www.alphavantage.co/query',
            'premium': False,
            'calls_per_minute': 5,
            'retry_attempts': 2,
            'timeout': 30
        }
        
        # 🔐 Configuración de Yahoo Finance (Backup)
        self.YAHOO_FINANCE_CONFIG = {
            'enabled': True,
            'base_url': 'https://query1.finance.yahoo.com/v8/finance/chart/',
            'symbols_mapping': {
                'EURUSD': 'EURUSD=X',
                'GBPUSD': 'GBPUSD=X',
                'USDJPY': 'USDJPY=X',
                'AUDUSD': 'AUDUSD=X',
                'USDCAD': 'USDCAD=X'
            },
            'timeout': 15,
            'retry_attempts': 2
        }
        
        # 🔐 Configuración de Datos Simulados (Desarrollo)
        self.SIMULATION_CONFIG = {
            'enabled': True,
            'base_price': {
                'EURUSD': 1.0900,
                'GBPUSD': 1.2700,
                'USDJPY': 145.50,
                'AUDUSD': 0.6600,
                'USDCAD': 1.3500
            },
            'volatility': {
                'EURUSD': 0.0010,
                'GBPUSD': 0.0015,
                'USDJPY': 0.5000,
                'AUDUSD': 0.0012,
                'USDCAD': 0.0008
            },
            'trend_bias': 0.0001  # Sesgo alcista/bajista
        }
        
        # 🎯 Configuración de Prioridades
        self.DATA_SOURCE_PRIORITY = [
            'MT5',              # Primera opción
            'ALPHA_VANTAGE',    # Segunda opción
            'YAHOO_FINANCE',    # Tercera opción
            'SIMULATION'        # Último recurso
        ]
        
        # ⚡ Configuración de Cache
        self.CACHE_CONFIG = {
            'enabled': True,
            'ttl_seconds': {
                'M1': 60,       # 1 minuto
                'M5': 300,      # 5 minutos
                'M15': 900,     # 15 minutos
                'H1': 3600,     # 1 hora
                'H4': 14400,    # 4 horas
                'D1': 86400     # 1 día
            },
            'max_size_mb': 100,
            'cleanup_interval': 3600
        }
        
    def get_active_source(self) -> str:
        """Obtener la fuente de datos activa según prioridad"""
        for source in self.DATA_SOURCE_PRIORITY:
            config = getattr(self, f'{source}_CONFIG', {})
            if config.get('enabled', False):
                return source
        return 'SIMULATION'  # Fallback
    
    def get_source_config(self, source: str) -> Dict[str, Any]:
        """Obtener configuración de una fuente específica"""
        config_attr = f'{source}_CONFIG'
        return getattr(self, config_attr, {})
    
    def is_source_available(self, source: str) -> bool:
        """Verificar si una fuente está disponible"""
        config = self.get_source_config(source)
        return config.get('enabled', False)
    
    def get_fallback_chain(self) -> list:
        """Obtener cadena de fallback de fuentes de datos"""
        return [source for source in self.DATA_SOURCE_PRIORITY 
                if self.is_source_available(source)]


# Instancia global
DATA_SOURCES = DataSourcesConfig()


def validate_data_sources() -> Dict[str, Any]:
    """
    🔍 Validar todas las fuentes de datos configuradas
    
    Returns:
        dict: Estado de validación de cada fuente
    """
    validation_results = {
        'timestamp': '2025-08-13T19:00:00',
        'sources': {},
        'active_source': DATA_SOURCES.get_active_source(),
        'fallback_chain': DATA_SOURCES.get_fallback_chain()
    }
    
    for source in DATA_SOURCES.DATA_SOURCE_PRIORITY:
        config = DATA_SOURCES.get_source_config(source)
        
        validation = {
            'enabled': config.get('enabled', False),
            'configured': True,
            'credentials_set': False,
            'status': 'unknown'
        }
        
        # Validaciones específicas por fuente
        if source == 'MT5':
            validation['credentials_set'] = (
                config.get('login', 0) > 0 and 
                len(config.get('password', '')) > 0
            )
            validation['status'] = 'ready' if validation['credentials_set'] else 'needs_credentials'
            
        elif source == 'ALPHA_VANTAGE':
            validation['credentials_set'] = (
                config.get('api_key', 'demo') != 'demo'
            )
            validation['status'] = 'ready' if validation['credentials_set'] else 'needs_api_key'
            
        elif source == 'YAHOO_FINANCE':
            validation['credentials_set'] = True  # No requiere credenciales
            validation['status'] = 'ready'
            
        elif source == 'SIMULATION':
            validation['credentials_set'] = True  # Siempre disponible
            validation['status'] = 'ready'
        
        validation_results['sources'][source] = validation
    
    return validation_results


if __name__ == "__main__":
    # Test de configuración
    print("🌐 Configuración de Fuentes de Datos - Trading Grid")
    print("=" * 60)
    
    validation = validate_data_sources()
    
    print(f"📊 Fuente activa: {validation['active_source']}")
    print(f"🔄 Cadena de fallback: {' -> '.join(validation['fallback_chain'])}")
    print()
    
    for source, status in validation['sources'].items():
        enabled = "✅" if status['enabled'] else "❌"
        credentials = "🔐" if status['credentials_set'] else "🔓"
        print(f"{enabled} {credentials} {source}: {status['status']}")
