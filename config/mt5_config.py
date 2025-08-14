"""
🏢 CONFIGURACIÓN MT5 PURA - TRADING GRID
=======================================

Configuración directa y profesional SOLO para MetaTrader 5
Sin simulaciones, sin confusiones - SOLO TRADING REAL

AUTOR: Trading Grid System
FECHA: 2025-08-13
VERSIÓN: 1.0.0 - MT5 ONLY
"""

import os
import MetaTrader5 as mt5
from datetime import datetime
from typing import Dict, Any, Optional

class MT5Config:
    """Configuración pura de MT5 - SOLO TRADING REAL"""
    
    def __init__(self):
        # 🔐 Configuración MT5 - ÚNICA FUENTE
        self.MT5_CREDENTIALS = {
            'login': int(os.getenv('MT5_LOGIN', '0')),
            'password': os.getenv('MT5_PASSWORD', ''),
            'server': os.getenv('MT5_SERVER', 'MetaQuotes-Demo'),
            'path': os.getenv('MT5_PATH', ''),
            'timeout': 60000,
            'retry_attempts': 3
        }
        
        # 📊 Configuración de Trading
        self.TRADING_CONFIG = {
            'symbols': ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD'],
            'primary_symbol': 'EURUSD',
            'timeframes': {
                'M1': mt5.TIMEFRAME_M1,
                'M5': mt5.TIMEFRAME_M5,
                'M15': mt5.TIMEFRAME_M15,
                'H1': mt5.TIMEFRAME_H1,
                'H4': mt5.TIMEFRAME_H4,
                'D1': mt5.TIMEFRAME_D1
            },
            'default_timeframe': 'H1'
        }
        
        # 🎯 Configuración de Órdenes
        self.ORDER_CONFIG = {
            'deviation': 10,        # Slippage máximo en puntos
            'magic_number': 987654, # Número mágico único
            'fill_policy': mt5.ORDER_FILLING_IOC,
            'type_time': mt5.ORDER_TIME_GTC,
            'retry_attempts': 3,
            'retry_delay': 1.0
        }
        
        # Estado del sistema
        self.is_connected = False
        self.connection_info = {}
        self.last_check = None
    
    def connect_mt5(self) -> bool:
        """
        🔌 Conectar a MT5 - FUNCIÓN PRINCIPAL
        
        Returns:
            bool: True si conexión exitosa
        """
        try:
            print("🔌 Conectando a MetaTrader 5...")
            
            # Inicializar MT5
            if not mt5.initialize(
                path=self.MT5_CREDENTIALS['path'] if self.MT5_CREDENTIALS['path'] else None,
                login=self.MT5_CREDENTIALS['login'] if self.MT5_CREDENTIALS['login'] > 0 else None,
                password=self.MT5_CREDENTIALS['password'] if self.MT5_CREDENTIALS['password'] else None,
                server=self.MT5_CREDENTIALS['server'] if self.MT5_CREDENTIALS['server'] != 'MetaQuotes-Demo' else None,
                timeout=self.MT5_CREDENTIALS['timeout']
            ):
                error = mt5.last_error()
                print(f"❌ Error inicializando MT5: {error}")
                return False
            
            # Obtener información de la conexión
            account_info = mt5.account_info()
            if account_info is None:
                print("❌ No se pudo obtener información de cuenta MT5")
                mt5.shutdown()
                return False
            
            # Guardar información de conexión
            self.connection_info = {
                'login': account_info.login,
                'server': account_info.server,
                'currency': account_info.currency,
                'balance': account_info.balance,
                'equity': account_info.equity,
                'margin': account_info.margin,
                'margin_free': account_info.margin_free,
                'company': account_info.company,
                'name': account_info.name
            }
            
            self.is_connected = True
            self.last_check = datetime.now()
            
            print("✅ MT5 conectado exitosamente")
            print(f"   📊 Cuenta: {account_info.login}")
            print(f"   🏦 Servidor: {account_info.server}")
            print(f"   💰 Balance: ${account_info.balance:.2f}")
            print(f"   🏢 Broker: {account_info.company}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error conectando MT5: {e}")
            self.is_connected = False
            return False
    
    def disconnect_mt5(self):
        """🔌 Desconectar MT5"""
        try:
            if self.is_connected:
                mt5.shutdown()
                self.is_connected = False
                print("🔌 MT5 desconectado")
        except Exception as e:
            print(f"⚠️ Error desconectando MT5: {e}")
    
    def check_connection(self) -> bool:
        """✅ Verificar estado de conexión MT5"""
        try:
            if not self.is_connected:
                return False
            
            # Verificar con una consulta simple
            account_info = mt5.account_info()
            if account_info is None:
                self.is_connected = False
                return False
            
            self.last_check = datetime.now()
            return True
            
        except Exception as e:
            print(f"⚠️ Error verificando conexión MT5: {e}")
            self.is_connected = False
            return False
    
    def get_symbols_info(self) -> Dict[str, Any]:
        """📊 Obtener información de símbolos"""
        try:
            if not self.check_connection():
                return {}
            
            symbols_info = {}
            for symbol in self.TRADING_CONFIG['symbols']:
                info = mt5.symbol_info(symbol)
                if info is not None:
                    symbols_info[symbol] = {
                        'bid': info.bid,
                        'ask': info.ask,
                        'spread': info.spread,
                        'point': info.point,
                        'digits': info.digits,
                        'trade_mode': info.trade_mode,
                        'volume_min': info.volume_min,
                        'volume_max': info.volume_max,
                        'volume_step': info.volume_step
                    }
            
            return symbols_info
            
        except Exception as e:
            print(f"❌ Error obteniendo información de símbolos: {e}")
            return {}
    
    def get_market_data(self, symbol: str, timeframe: str, count: int = 100) -> Optional[Any]:
        """
        📊 Obtener datos de mercado MT5
        
        Args:
            symbol: Par de divisas
            timeframe: Marco temporal (M1, M5, M15, H1, H4, D1)
            count: Número de velas
            
        Returns:
            Datos de mercado o None
        """
        try:
            if not self.check_connection():
                print("❌ MT5 no conectado")
                return None
            
            # Obtener timeframe MT5
            mt5_timeframe = self.TRADING_CONFIG['timeframes'].get(timeframe, mt5.TIMEFRAME_H1)
            
            # Obtener datos
            rates = mt5.copy_rates_from_pos(symbol, mt5_timeframe, 0, count)
            
            if rates is None or len(rates) == 0:
                print(f"❌ No se obtuvieron datos para {symbol} {timeframe}")
                return None
            
            print(f"✅ Datos obtenidos: {symbol} {timeframe} ({len(rates)} velas)")
            return rates
            
        except Exception as e:
            print(f"❌ Error obteniendo datos de mercado: {e}")
            return None
    
    def place_order(self, symbol: str, order_type: int, volume: float, price: float, 
                   sl: float = 0.0, tp: float = 0.0, comment: str = "") -> Optional[Any]:
        """
        💹 Colocar orden en MT5
        
        Args:
            symbol: Par de divisas
            order_type: Tipo de orden MT5
            volume: Volumen en lotes
            price: Precio de entrada
            sl: Stop Loss
            tp: Take Profit
            comment: Comentario
            
        Returns:
            Resultado de la orden o None
        """
        try:
            if not self.check_connection():
                print("❌ MT5 no conectado")
                return None
            
            # Preparar solicitud
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": volume,
                "type": order_type,
                "price": price,
                "sl": sl,
                "tp": tp,
                "deviation": self.ORDER_CONFIG['deviation'],
                "magic": self.ORDER_CONFIG['magic_number'],
                "comment": comment,
                "type_time": self.ORDER_CONFIG['type_time'],
                "type_filling": self.ORDER_CONFIG['fill_policy'],
            }
            
            # Enviar orden
            result = mt5.order_send(request)
            
            if result is None:
                print("❌ Error enviando orden")
                return None
            
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                print(f"✅ Orden ejecutada: {symbol} {volume} lotes")
                print(f"   📊 Ticket: {result.order}")
                print(f"   💰 Precio: {result.price}")
                return result
            else:
                print(f"❌ Error en orden: {result.retcode} - {result.comment}")
                return None
            
        except Exception as e:
            print(f"❌ Error colocando orden: {e}")
            return None
    
    def get_positions(self) -> list:
        """📊 Obtener posiciones abiertas"""
        try:
            if not self.check_connection():
                return []
            
            positions = mt5.positions_get()
            if positions is None:
                return []
            
            return list(positions)
            
        except Exception as e:
            print(f"❌ Error obteniendo posiciones: {e}")
            return []
    
    def get_status(self) -> Dict[str, Any]:
        """📊 Obtener estado completo de MT5"""
        return {
            'connected': self.is_connected,
            'connection_info': self.connection_info,
            'last_check': self.last_check.isoformat() if self.last_check else None,
            'symbols_count': len(self.TRADING_CONFIG['symbols']),
            'primary_symbol': self.TRADING_CONFIG['primary_symbol'],
            'timestamp': datetime.now().isoformat()
        }


# Instancia global
MT5_SYSTEM = MT5Config()


def validate_mt5_setup() -> Dict[str, Any]:
    """
    ✅ Validar configuración completa de MT5
    
    Returns:
        dict: Estado de validación
    """
    validation = {
        'timestamp': datetime.now().isoformat(),
        'mt5_available': False,
        'connection_status': 'disconnected',
        'credentials_configured': False,
        'symbols_accessible': 0,
        'ready_for_trading': False,
        'issues': []
    }
    
    try:
        # Verificar si MT5 está disponible
        try:
            import MetaTrader5 as mt5
            validation['mt5_available'] = True
        except ImportError:
            validation['issues'].append('MetaTrader5 no está instalado')
            return validation
        
        # Verificar credenciales
        credentials = MT5_SYSTEM.MT5_CREDENTIALS
        if credentials['login'] > 0 and credentials['password']:
            validation['credentials_configured'] = True
        else:
            validation['issues'].append('Credenciales MT5 no configuradas')
        
        # Intentar conexión
        if MT5_SYSTEM.connect_mt5():
            validation['connection_status'] = 'connected'
            
            # Verificar símbolos
            symbols_info = MT5_SYSTEM.get_symbols_info()
            validation['symbols_accessible'] = len(symbols_info)
            
            if validation['symbols_accessible'] > 0:
                validation['ready_for_trading'] = True
            else:
                validation['issues'].append('No se pueden acceder a símbolos de trading')
        else:
            validation['issues'].append('No se pudo conectar a MT5')
    
    except Exception as e:
        validation['issues'].append(f'Error general: {e}')
    
    return validation


if __name__ == "__main__":
    print("🏢 MT5 Configuration - Trading Grid")
    print("=" * 50)
    
    # Validar configuración
    validation = validate_mt5_setup()
    
    print(f"📊 MT5 disponible: {'✅' if validation['mt5_available'] else '❌'}")
    print(f"🔐 Credenciales: {'✅' if validation['credentials_configured'] else '❌'}")
    print(f"🔌 Conexión: {validation['connection_status']}")
    print(f"📈 Símbolos accesibles: {validation['symbols_accessible']}")
    print(f"💹 Listo para trading: {'✅' if validation['ready_for_trading'] else '❌'}")
    
    if validation['issues']:
        print(f"\n⚠️ Problemas detectados:")
        for issue in validation['issues']:
            print(f"   - {issue}")
    
    # Limpiar conexión
    MT5_SYSTEM.disconnect_mt5()
