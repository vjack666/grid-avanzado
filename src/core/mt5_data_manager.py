"""
🏢 MT5 DATA MANAGER - TRADING GRID
================================

Gestor de datos profesional EXCLUSIVAMENTE con MetaTrader 5
Datos directos del broker en tiempo real - CONFIGURACIÓN LIMPIA

CARACTERÍSTICAS:
- ✅ Conexión directa MT5
- ✅ Datos en tiempo real
- ✅ Múltiples timeframes
- ✅ Gestión de órdenes
- ✅ Monitoreo de posiciones
- ✅ Cache inteligente

AUTOR: Trading Grid System
VERSIÓN: 2.0 - MT5 ONLY
FECHA: 2025-08-13
"""

import sys
from pathlib import Path
import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
import pandas as pd
import numpy as np

# Configurar imports del proyecto
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root.absolute()))

from config.mt5_config import MT5_SYSTEM
from src.core.logger_manager import LoggerManager

class MT5DataManager:
    """
    🏢 GESTOR DE DATOS MT5 - PROFESIONAL
    
    Funcionalidades:
    - Datos de mercado en tiempo real
    - Gestión de órdenes y posiciones
    - Cache inteligente
    - Reconexión automática
    - Validación de datos
    """
    
    def __init__(self):
        self.logger = LoggerManager().get_logger('mt5_data_manager')
        
        # Cache de datos
        self.data_cache = {}
        self.cache_expiry = {}
        self.cache_duration = {
            'M1': 30,    # 30 segundos
            'M5': 60,    # 1 minuto
            'M15': 180,  # 3 minutos
            'H1': 600,   # 10 minutos
            'H4': 1800,  # 30 minutos
            'D1': 3600   # 1 hora
        }
        
        # Estado del sistema
        self.is_initialized = False
        self.last_error = None
        self.connection_attempts = 0
        self.max_reconnect_attempts = 5
        
        # Estadísticas
        self.stats = {
            'total_requests': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'errors': 0,
            'last_update': None
        }
        
        self.logger.info("🏢 MT5DataManager inicializado")
    
    async def initialize(self) -> bool:
        """
        🚀 Inicializar conexión MT5
        
        Returns:
            bool: True si inicialización exitosa
        """
        try:
            self.logger.info("🚀 Inicializando conexión MT5...")
            
            if MT5_SYSTEM.connect_mt5():
                self.is_initialized = True
                self.connection_attempts = 0
                self.logger.info("✅ MT5 conectado y listo")
                return True
            else:
                self.logger.error("❌ Error conectando MT5")
                return False
                
        except Exception as e:
            self.logger.error("❌ Error inicializando MT5: %s", e)
            self.last_error = str(e)
            return False
    
    async def ensure_connection(self) -> bool:
        """🔄 Asegurar conexión activa"""
        try:
            if not self.is_initialized:
                return await self.initialize()
            
            # Verificar conexión
            if not MT5_SYSTEM.check_connection():
                self.logger.warning("⚠️ Conexión MT5 perdida - Reconectando...")
                self.is_initialized = False
                return await self.initialize()
            
            return True
            
        except Exception as e:
            self.logger.error("❌ Error verificando conexión: %s", e)
            return False
    
    def _get_cache_key(self, symbol: str, timeframe: str, count: int) -> str:
        """🔑 Generar clave de cache"""
        return f"{symbol}_{timeframe}_{count}"
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """✅ Verificar si cache es válido"""
        if cache_key not in self.cache_expiry:
            return False
        
        return time.time() < self.cache_expiry[cache_key]
    
    def _cache_data(self, cache_key: str, data: Any, timeframe: str):
        """💾 Guardar datos en cache"""
        self.data_cache[cache_key] = data
        expiry_seconds = self.cache_duration.get(timeframe, 300)
        self.cache_expiry[cache_key] = time.time() + expiry_seconds
    
    async def get_market_data(self, symbol: str, timeframe: str = 'H1', 
                            count: int = 100, use_cache: bool = True) -> Optional[pd.DataFrame]:
        """
        📊 Obtener datos de mercado MT5
        
        Args:
            symbol: Par de divisas (ej: 'EURUSD')
            timeframe: Marco temporal ('M1', 'M5', 'M15', 'H1', 'H4', 'D1')
            count: Número de velas
            use_cache: Usar cache si está disponible
            
        Returns:
            DataFrame con datos OHLCV o None
        """
        try:
            self.stats['total_requests'] += 1
            
            # Verificar cache
            cache_key = self._get_cache_key(symbol, timeframe, count)
            
            if use_cache and self._is_cache_valid(cache_key):
                self.stats['cache_hits'] += 1
                self.logger.info("💾 Datos obtenidos de cache: %s %s", symbol, timeframe)
                return self.data_cache[cache_key]
            
            self.stats['cache_misses'] += 1
            
            # Asegurar conexión
            if not await self.ensure_connection():
                self.logger.error("❌ No se pudo conectar a MT5")
                return None
            
            # Obtener datos de MT5
            raw_data = MT5_SYSTEM.get_market_data(symbol, timeframe, count)
            
            if raw_data is None:
                self.logger.error("❌ No se obtuvieron datos de %s %s", symbol, timeframe)
                self.stats['errors'] += 1
                return None
            
            # Convertir a DataFrame
            df = pd.DataFrame(raw_data)
            
            if len(df) == 0:
                self.logger.warning("⚠️ DataFrame vacío para %s %s", symbol, timeframe)
                return None
            
            # Procesar datos
            df['time'] = pd.to_datetime(df['time'], unit='s')
            df.set_index('time', inplace=True)
            df.columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'Spread', 'Real Volume']
            
            # Guardar en cache
            if use_cache:
                self._cache_data(cache_key, df.copy(), timeframe)
            
            self.stats['last_update'] = datetime.now()
            
            self.logger.info("✅ Datos obtenidos: %s %s (%d velas)", symbol, timeframe, len(df))
            return df
            
        except Exception as e:
            self.logger.error("❌ Error obteniendo datos de mercado: %s", e)
            self.stats['errors'] += 1
            self.last_error = str(e)
            return None
    
    async def get_real_time_quote(self, symbol: str) -> Optional[Dict[str, float]]:
        """
        💹 Obtener cotización en tiempo real
        
        Args:
            symbol: Par de divisas
            
        Returns:
            dict: Bid, Ask, Spread, etc.
        """
        try:
            if not await self.ensure_connection():
                return None
            
            symbols_info = MT5_SYSTEM.get_symbols_info()
            
            if symbol not in symbols_info:
                self.logger.error("❌ Símbolo no disponible: %s", symbol)
                return None
            
            symbol_data = symbols_info[symbol]
            
            quote = {
                'symbol': symbol,
                'bid': symbol_data['bid'],
                'ask': symbol_data['ask'],
                'spread': symbol_data['spread'],
                'point': symbol_data['point'],
                'digits': symbol_data['digits'],
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info("💹 Cotización %s: Bid=%.5f Ask=%.5f", 
                           symbol, quote['bid'], quote['ask'])
            
            return quote
            
        except Exception as e:
            self.logger.error("❌ Error obteniendo cotización: %s", e)
            return None
    
    async def get_multiple_symbols_data(self, symbols: List[str], timeframe: str = 'H1') -> Dict[str, pd.DataFrame]:
        """
        📊 Obtener datos de múltiples símbolos
        
        Args:
            symbols: Lista de pares de divisas
            timeframe: Marco temporal
            
        Returns:
            dict: Datos por símbolo
        """
        try:
            results = {}
            
            tasks = []
            for symbol in symbols:
                task = self.get_market_data(symbol, timeframe)
                tasks.append((symbol, task))
            
            # Ejecutar en paralelo
            for symbol, task in tasks:
                data = await task
                if data is not None:
                    results[symbol] = data
                    self.logger.info("✅ Datos obtenidos para %s", symbol)
                else:
                    self.logger.warning("⚠️ Sin datos para %s", symbol)
            
            return results
            
        except Exception as e:
            self.logger.error("❌ Error obteniendo datos múltiples: %s", e)
            return {}
    
    async def place_trade_order(self, symbol: str, order_type: str, volume: float, 
                              price: Optional[float] = None, sl: float = 0.0, 
                              tp: float = 0.0, comment: str = "") -> Optional[Dict[str, Any]]:
        """
        💹 Colocar orden de trading
        
        Args:
            symbol: Par de divisas
            order_type: 'BUY' o 'SELL'
            volume: Volumen en lotes
            price: Precio específico (None para market order)
            sl: Stop Loss
            tp: Take Profit
            comment: Comentario
            
        Returns:
            dict: Resultado de la orden
        """
        try:
            if not await self.ensure_connection():
                return None
            
            # Importar tipos MT5
            import MetaTrader5 as mt5
            
            # Convertir tipo de orden
            if order_type.upper() == 'BUY':
                mt5_order_type = mt5.ORDER_TYPE_BUY
                if price is None:
                    # Market buy - usar precio ask
                    quote = await self.get_real_time_quote(symbol)
                    if quote:
                        price = quote['ask']
                    else:
                        self.logger.error("❌ No se pudo obtener precio para %s", symbol)
                        return None
            elif order_type.upper() == 'SELL':
                mt5_order_type = mt5.ORDER_TYPE_SELL
                if price is None:
                    # Market sell - usar precio bid
                    quote = await self.get_real_time_quote(symbol)
                    if quote:
                        price = quote['bid']
                    else:
                        self.logger.error("❌ No se pudo obtener precio para %s", symbol)
                        return None
            else:
                self.logger.error("❌ Tipo de orden inválido: %s", order_type)
                return None
            
            # Colocar orden
            result = MT5_SYSTEM.place_order(symbol, mt5_order_type, volume, price, sl, tp, comment)
            
            if result is not None:
                order_data = {
                    'success': True,
                    'order_id': result.order,
                    'symbol': symbol,
                    'type': order_type,
                    'volume': volume,
                    'price': result.price,
                    'sl': sl,
                    'tp': tp,
                    'comment': comment,
                    'timestamp': datetime.now().isoformat()
                }
                
                self.logger.info("✅ Orden ejecutada: %s %s %.2f lotes @ %.5f", 
                               symbol, order_type, volume, result.price)
                return order_data
            else:
                self.logger.error("❌ Error ejecutando orden %s %s", symbol, order_type)
                return None
            
        except Exception as e:
            self.logger.error("❌ Error colocando orden: %s", e)
            return None
    
    async def get_account_info(self) -> Optional[Dict[str, Any]]:
        """
        💰 Obtener información de cuenta
        
        Returns:
            dict: Información de cuenta MT5
        """
        try:
            if not await self.ensure_connection():
                return None
            
            status = MT5_SYSTEM.get_status()
            
            if status['connected']:
                account_data = {
                    'connected': True,
                    'login': status['connection_info'].get('login'),
                    'server': status['connection_info'].get('server'),
                    'balance': status['connection_info'].get('balance'),
                    'equity': status['connection_info'].get('equity'),
                    'margin': status['connection_info'].get('margin'),
                    'margin_free': status['connection_info'].get('margin_free'),
                    'currency': status['connection_info'].get('currency'),
                    'company': status['connection_info'].get('company'),
                    'timestamp': datetime.now().isoformat()
                }
                
                return account_data
            else:
                return {'connected': False, 'error': 'MT5 no conectado'}
            
        except Exception as e:
            self.logger.error("❌ Error obteniendo info de cuenta: %s", e)
            return None
    
    async def get_open_positions(self) -> List[Dict[str, Any]]:
        """
        📊 Obtener posiciones abiertas
        
        Returns:
            list: Lista de posiciones abiertas
        """
        try:
            if not await self.ensure_connection():
                return []
            
            positions = MT5_SYSTEM.get_positions()
            
            positions_data = []
            for pos in positions:
                position_data = {
                    'ticket': pos.ticket,
                    'symbol': pos.symbol,
                    'type': 'BUY' if pos.type == 0 else 'SELL',
                    'volume': pos.volume,
                    'price_open': pos.price_open,
                    'price_current': pos.price_current,
                    'profit': pos.profit,
                    'comment': pos.comment,
                    'time': datetime.fromtimestamp(pos.time).isoformat()
                }
                positions_data.append(position_data)
            
            self.logger.info("📊 Posiciones abiertas: %d", len(positions_data))
            return positions_data
            
        except Exception as e:
            self.logger.error("❌ Error obteniendo posiciones: %s", e)
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """📈 Obtener estadísticas del sistema"""
        cache_hit_rate = 0
        if self.stats['total_requests'] > 0:
            cache_hit_rate = (self.stats['cache_hits'] / self.stats['total_requests']) * 100
        
        return {
            'mt5_connected': self.is_initialized and MT5_SYSTEM.is_connected,
            'total_requests': self.stats['total_requests'],
            'cache_hits': self.stats['cache_hits'],
            'cache_misses': self.stats['cache_misses'],
            'cache_hit_rate': f"{cache_hit_rate:.1f}%",
            'errors': self.stats['errors'],
            'last_error': self.last_error,
            'last_update': self.stats['last_update'].isoformat() if self.stats['last_update'] else None,
            'cache_entries': len(self.data_cache),
            'connection_attempts': self.connection_attempts
        }
    
    def clear_cache(self):
        """🧹 Limpiar cache"""
        self.data_cache.clear()
        self.cache_expiry.clear()
        self.logger.info("🧹 Cache limpiado")
    
    async def shutdown(self):
        """🔌 Cerrar conexiones y limpiar recursos"""
        try:
            MT5_SYSTEM.disconnect_mt5()
            self.clear_cache()
            self.is_initialized = False
            self.logger.info("🔌 MT5DataManager desconectado")
        except Exception as e:
            self.logger.error("❌ Error en shutdown: %s", e)


# Instancia global
DATA_MANAGER = MT5DataManager()


async def test_mt5_data_manager():
    """🧪 Prueba completa del MT5DataManager"""
    print("🏢 Testing MT5 Data Manager")
    print("=" * 50)
    
    # Inicializar
    if await DATA_MANAGER.initialize():
        print("✅ MT5DataManager inicializado")
        
        # Obtener cotización en tiempo real
        quote = await DATA_MANAGER.get_real_time_quote('EURUSD')
        if quote:
            print(f"💹 EURUSD: Bid={quote['bid']:.5f} Ask={quote['ask']:.5f}")
        
        # Obtener datos históricos
        data = await DATA_MANAGER.get_market_data('EURUSD', 'H1', 50)
        if data is not None:
            print(f"📊 Datos históricos EURUSD H1: {len(data)} velas")
            print(f"   Último close: {data['Close'].iloc[-1]:.5f}")
        
        # Información de cuenta
        account = await DATA_MANAGER.get_account_info()
        if account and account.get('connected'):
            print(f"💰 Cuenta: {account.get('login')} - Balance: ${account.get('balance', 0):.2f}")
        
        # Estadísticas
        stats = DATA_MANAGER.get_statistics()
        print(f"📈 Requests: {stats['total_requests']} - Errors: {stats['errors']}")
        print(f"💾 Cache hit rate: {stats['cache_hit_rate']}")
        
        # Limpiar
        await DATA_MANAGER.shutdown()
    else:
        print("❌ Error inicializando MT5DataManager")


if __name__ == "__main__":
    asyncio.run(test_mt5_data_manager())
