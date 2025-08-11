"""
MT5Manager - Gestor centralizado de MetaTrader 5
==============================================

Centraliza toda la lógica de conectividad MT5, gestión de órdenes y posiciones.
Parte del protocolo de modularización Trading Grid.

Autor: Trading Grid System
Fecha: 2025-08-10
Fase: 6/6 - MT5Manager (Fase Final)
"""

import MetaTrader5 as mt5
from typing import Dict, List, Optional, Union, Any
from datetime import datetime
import time


class MT5Manager:
    """
    Gestor centralizado de MetaTrader 5
    
    Centraliza:
    - Conectividad y gestión de conexión
    - Gestión de órdenes (envío, modificación, cancelación)
    - Gestión de posiciones (obtención, cierre, modificación)
    - Información de mercado (precios, símbolos, estado)
    """
    
    def __init__(self, config_manager, logger_manager, error_manager):
        """
        Inicializa MT5Manager
        
        Args:
            config_manager: Gestor de configuración
            logger_manager: Gestor de logging
            error_manager: Gestor de errores
        """
        self.config = config_manager
        self.logger = logger_manager
        self.error = error_manager
        
        # Estado de conexión
        self._is_connected = False
        self._account_info = None
        self._last_connection_check = 0
        self._connection_check_interval = 30  # segundos
        
        # Cache de información
        self._symbol_info_cache = {}
        self._cache_timeout = 60  # segundos
        
        self.logger.log_info("MT5Manager inicializado")
    
    # =================================================================
    # GESTIÓN DE CONECTIVIDAD
    # =================================================================
    
    def connect(self) -> bool:
        """
        Establece conexión con MT5
        
        Returns:
            bool: True si conexión exitosa, False en caso contrario
        """
        try:
            self.logger.log_info("Iniciando conexión a MT5...")
            
            # Intentar inicializar MT5
            if not mt5.initialize():
                error_msg = f"Error al inicializar MT5: {mt5.last_error()}"
                self.error.log_error("MT5_CONNECTION_ERROR", error_msg, 
                                   {"error_code": mt5.last_error()})
                return False
            
            # Verificar información de la cuenta
            account_info = mt5.account_info()
            if account_info is None:
                error_msg = f"No se pudo obtener información de cuenta: {mt5.last_error()}"
                self.error.log_error("MT5_ACCOUNT_ERROR", error_msg,
                                   {"error_code": mt5.last_error()})
                return False
            
            self._account_info = account_info._asdict()
            self._is_connected = True
            self._last_connection_check = time.time()
            
            self.logger.log_success("Conexión a MT5 establecida exitosamente")
            return True
            
        except Exception as e:
            self.error.log_error("MT5_CONNECTION_EXCEPTION", f"Excepción al conectar: {str(e)}", 
                               {"exception": str(e)})
            return False
    
    def disconnect(self) -> bool:
        """
        Desconecta de MT5
        
        Returns:
            bool: True si desconexión exitosa
        """
        try:
            self.logger.log_info("Desconectando de MT5...")
            
            mt5.shutdown()
            self._is_connected = False
            self._account_info = None
            
            self.logger.log_success("Desconexión de MT5 completada")
            return True
            
        except Exception as e:
            self.error.log_error("MT5_DISCONNECTION_ERROR", f"Error al desconectar: {str(e)}",
                               {"exception": str(e)})
            return False
    
    def is_connected(self) -> bool:
        """
        Verifica si MT5 está conectado
        
        Returns:
            bool: True si conectado y operativo
        """
        try:
            # Si no tenemos estado de conexión, retornar False
            if not self._is_connected:
                return False
                
            # Verificar si necesitamos revisar la conexión
            current_time = time.time()
            if current_time - self._last_connection_check > self._connection_check_interval:
                # Verificar estado real de MT5
                try:
                    terminal_info = mt5.terminal_info()
                    if terminal_info is None or not terminal_info.connected:
                        self._is_connected = False
                    else:
                        self._is_connected = True
                except:
                    # Si hay cualquier error al verificar MT5, asumir desconectado
                    self._is_connected = False
                
                self._last_connection_check = current_time
            
            return self._is_connected
            
        except Exception as e:
            self.error.log_error("MT5_CONNECTION_CHECK_ERROR", 
                               f"Error al verificar conexión: {str(e)}",
                               {"exception": str(e)})
            self._is_connected = False
            return False
    
    def reconnect(self) -> bool:
        """
        Intenta reconectar a MT5
        
        Returns:
            bool: True si reconexión exitosa
        """
        self.logger.warning("Intentando reconexión a MT5...",
                          extra={"componente": "MT5Manager", "accion": "reconectar"})
        
        # Desconectar primero
        self.disconnect()
        
        # Esperar un momento
        time.sleep(2)
        
        # Intentar reconectar
        return self.connect()
    
    def get_account_info(self) -> Optional[Dict]:
        """
        Obtiene información de la cuenta
        
        Returns:
            dict: Información de cuenta o None si no está disponible
        """
        if not self.is_connected():
            self.logger.warning("No hay conexión para obtener información de cuenta",
                              extra={"componente": "MT5Manager", "accion": "get_account_info"})
            return None
        
        try:
            # Actualizar información de cuenta
            account_info = mt5.account_info()
            if account_info is not None:
                self._account_info = account_info._asdict()
                return self._account_info
            else:
                self.error.log_error("MT5_ACCOUNT_INFO_ERROR", 
                                   f"Error al obtener info de cuenta: {mt5.last_error()}",
                                   {"error_code": mt5.last_error()})
                return None
                
        except Exception as e:
            self.error.log_error("MT5_ACCOUNT_INFO_EXCEPTION", 
                               f"Excepción al obtener info de cuenta: {str(e)}",
                               {"exception": str(e)})
            return None
    
    # =================================================================
    # GESTIÓN DE ÓRDENES
    # =================================================================
    
    def send_order(self, symbol: str, order_type: int, volume: float, 
                   price: Optional[float] = None, sl: Optional[float] = None, 
                   tp: Optional[float] = None, comment: str = "Trading Grid") -> Dict:
        """
        Envía una orden a MT5
        
        Args:
            symbol: Símbolo del instrumento
            order_type: Tipo de orden (mt5.ORDER_TYPE_*)
            volume: Volumen de la orden
            price: Precio (para órdenes pending)
            sl: Stop Loss
            tp: Take Profit
            comment: Comentario de la orden
            
        Returns:
            dict: Resultado de la orden con información detallada
        """
        if not self.is_connected():
            return {
                "success": False,
                "error": "No hay conexión a MT5",
                "retcode": -1
            }
        
        try:
            # Validar símbolo
            symbol_info = self.get_symbol_info(symbol)
            if not symbol_info:
                return {
                    "success": False,
                    "error": f"Símbolo {symbol} no encontrado",
                    "retcode": -1
                }
            
            # Preparar solicitud de orden
            request = {
                "action": mt5.TRADE_ACTION_DEAL if order_type in [mt5.ORDER_TYPE_BUY, mt5.ORDER_TYPE_SELL] else mt5.TRADE_ACTION_PENDING,
                "symbol": symbol,
                "volume": volume,
                "type": order_type,
                "comment": comment,
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            # Añadir precio si es necesario
            if price is not None:
                request["price"] = price
            
            # Añadir SL/TP si están especificados
            if sl is not None:
                request["sl"] = sl
            if tp is not None:
                request["tp"] = tp
            
            # Enviar orden
            result = mt5.order_send(request)
            
            if result is None:
                return {
                    "success": False,
                    "error": f"Error en order_send: {mt5.last_error()}",
                    "retcode": mt5.last_error()[0] if mt5.last_error() else -1
                }
            
            # Procesar resultado
            result_dict = result._asdict()
            success = result_dict.get("retcode") == mt5.TRADE_RETCODE_DONE
            
            if success:
                self.logger.success(f"Orden enviada exitosamente: {symbol} {volume}",
                                  extra={
                                      "componente": "MT5Manager",
                                      "accion": "send_order",
                                      "symbol": symbol,
                                      "volume": volume,
                                      "order_type": order_type,
                                      "ticket": result_dict.get("order")
                                  })
            else:
                self.error.log_error("MT5_ORDER_ERROR", 
                                   f"Error al enviar orden: {result_dict.get('comment')}",
                                   {
                                       "symbol": symbol,
                                       "volume": volume,
                                       "retcode": result_dict.get("retcode"),
                                       "comment": result_dict.get("comment")
                                   })
            
            return {
                "success": success,
                "result": result_dict,
                "retcode": result_dict.get("retcode"),
                "comment": result_dict.get("comment"),
                "order": result_dict.get("order"),
                "deal": result_dict.get("deal")
            }
            
        except Exception as e:
            self.error.log_error("MT5_ORDER_EXCEPTION", f"Excepción al enviar orden: {str(e)}",
                               {
                                   "symbol": symbol,
                                   "volume": volume,
                                   "exception": str(e)
                               })
            return {
                "success": False,
                "error": f"Excepción: {str(e)}",
                "retcode": -1
            }
    
    def get_pending_orders(self, symbol: Optional[str] = None) -> List[Dict]:
        """
        Obtiene órdenes pendientes
        
        Args:
            symbol: Símbolo específico (opcional)
            
        Returns:
            list: Lista de órdenes pendientes
        """
        if not self.is_connected():
            return []
        
        try:
            orders = mt5.orders_get(symbol=symbol)
            if orders is None:
                return []
            
            return [order._asdict() for order in orders]
            
        except Exception as e:
            self.error.log_error("MT5_ORDERS_GET_EXCEPTION", 
                               f"Excepción al obtener órdenes: {str(e)}",
                               {"symbol": symbol, "exception": str(e)})
            return []
    
    def cancel_order(self, ticket: int) -> bool:
        """
        Cancela una orden pendiente
        
        Args:
            ticket: Ticket de la orden
            
        Returns:
            bool: True si cancelación exitosa
        """
        if not self.is_connected():
            return False
        
        try:
            request = {
                "action": mt5.TRADE_ACTION_REMOVE,
                "order": ticket
            }
            
            result = mt5.order_send(request)
            if result is None:
                return False
            
            success = result.retcode == mt5.TRADE_RETCODE_DONE
            
            if success:
                self.logger.success(f"Orden {ticket} cancelada exitosamente",
                                  extra={
                                      "componente": "MT5Manager",
                                      "accion": "cancel_order",
                                      "ticket": ticket
                                  })
            else:
                self.error.log_error("MT5_CANCEL_ERROR", 
                                   f"Error al cancelar orden {ticket}: {result.comment}",
                                   {"ticket": ticket, "retcode": result.retcode})
            
            return success
            
        except Exception as e:
            self.error.log_error("MT5_CANCEL_EXCEPTION", 
                               f"Excepción al cancelar orden {ticket}: {str(e)}",
                               {"ticket": ticket, "exception": str(e)})
            return False
    
    # =================================================================
    # GESTIÓN DE POSICIONES
    # =================================================================
    
    def get_positions(self, symbol: Optional[str] = None) -> List[Dict]:
        """
        Obtiene posiciones abiertas
        
        Args:
            symbol: Símbolo específico (opcional)
            
        Returns:
            list: Lista de posiciones abiertas
        """
        if not self.is_connected():
            return []
        
        try:
            positions = mt5.positions_get(symbol=symbol)
            if positions is None:
                return []
            
            return [position._asdict() for position in positions]
            
        except Exception as e:
            self.error.log_error("MT5_POSITIONS_GET_EXCEPTION", 
                               f"Excepción al obtener posiciones: {str(e)}",
                               {"symbol": symbol, "exception": str(e)})
            return []
    
    def close_position(self, ticket: int) -> bool:
        """
        Cierra una posición
        
        Args:
            ticket: Ticket de la posición
            
        Returns:
            bool: True si cierre exitoso
        """
        if not self.is_connected():
            return False
        
        try:
            # Obtener información de la posición
            position = mt5.positions_get(ticket=ticket)
            if not position:
                self.error.log_error("MT5_POSITION_NOT_FOUND", 
                                   f"Posición {ticket} no encontrada",
                                   {"ticket": ticket})
                return False
            
            position = position[0]
            
            # Determinar tipo de orden para cierre
            close_type = mt5.ORDER_TYPE_SELL if position.type == mt5.POSITION_TYPE_BUY else mt5.ORDER_TYPE_BUY
            
            # Crear solicitud de cierre
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": position.symbol,
                "volume": position.volume,
                "type": close_type,
                "position": ticket,
                "comment": "Trading Grid - Close"
            }
            
            result = mt5.order_send(request)
            if result is None:
                return False
            
            success = result.retcode == mt5.TRADE_RETCODE_DONE
            
            if success:
                self.logger.success(f"Posición {ticket} cerrada exitosamente",
                                  extra={
                                      "componente": "MT5Manager",
                                      "accion": "close_position",
                                      "ticket": ticket,
                                      "symbol": position.symbol,
                                      "volume": position.volume
                                  })
            else:
                self.error.log_error("MT5_CLOSE_ERROR", 
                                   f"Error al cerrar posición {ticket}: {result.comment}",
                                   {"ticket": ticket, "retcode": result.retcode})
            
            return success
            
        except Exception as e:
            self.error.log_error("MT5_CLOSE_EXCEPTION", 
                               f"Excepción al cerrar posición {ticket}: {str(e)}",
                               {"ticket": ticket, "exception": str(e)})
            return False
    
    def get_total_exposure(self, symbol: Optional[str] = None) -> Dict:
        """
        Calcula exposición total
        
        Args:
            symbol: Símbolo específico (opcional)
            
        Returns:
            dict: Información de exposición
        """
        positions = self.get_positions(symbol)
        
        exposure = {
            "total_volume": 0.0,
            "buy_volume": 0.0,
            "sell_volume": 0.0,
            "net_volume": 0.0,
            "positions_count": len(positions),
            "symbols": {}
        }
        
        for pos in positions:
            pos_symbol = pos.get("symbol")
            volume = pos.get("volume", 0)
            pos_type = pos.get("type")
            
            # Totales generales
            exposure["total_volume"] += volume
            
            if pos_type == mt5.POSITION_TYPE_BUY:
                exposure["buy_volume"] += volume
                exposure["net_volume"] += volume
            else:
                exposure["sell_volume"] += volume
                exposure["net_volume"] -= volume
            
            # Por símbolo
            if pos_symbol not in exposure["symbols"]:
                exposure["symbols"][pos_symbol] = {
                    "total_volume": 0.0,
                    "buy_volume": 0.0,
                    "sell_volume": 0.0,
                    "net_volume": 0.0,
                    "positions_count": 0
                }
            
            symbol_data = exposure["symbols"][pos_symbol]
            symbol_data["total_volume"] += volume
            symbol_data["positions_count"] += 1
            
            if pos_type == mt5.POSITION_TYPE_BUY:
                symbol_data["buy_volume"] += volume
                symbol_data["net_volume"] += volume
            else:
                symbol_data["sell_volume"] += volume
                symbol_data["net_volume"] -= volume
        
        return exposure
    
    # =================================================================
    # INFORMACIÓN DE MERCADO
    # =================================================================
    
    def get_current_price(self, symbol: str) -> Optional[Dict]:
        """
        Obtiene precio actual de un símbolo
        
        Args:
            symbol: Símbolo del instrumento
            
        Returns:
            dict: Información de precio o None si error
        """
        if not self.is_connected():
            return None
        
        try:
            tick = mt5.symbol_info_tick(symbol)
            if tick is None:
                return None
            
            return {
                "symbol": symbol,
                "bid": tick.bid,
                "ask": tick.ask,
                "spread": tick.ask - tick.bid,
                "time": datetime.fromtimestamp(tick.time),
                "last": tick.last,
                "volume": tick.volume
            }
            
        except Exception as e:
            self.error.log_error("MT5_PRICE_EXCEPTION", 
                               f"Excepción al obtener precio de {symbol}: {str(e)}",
                               {"symbol": symbol, "exception": str(e)})
            return None
    
    def get_symbol_info(self, symbol: str) -> Optional[Dict]:
        """
        Obtiene información de un símbolo con cache
        
        Args:
            symbol: Símbolo del instrumento
            
        Returns:
            dict: Información del símbolo o None si error
        """
        if not self.is_connected():
            return None
        
        try:
            # Verificar cache
            current_time = time.time()
            if symbol in self._symbol_info_cache:
                cached_data, cache_time = self._symbol_info_cache[symbol]
                if current_time - cache_time < self._cache_timeout:
                    return cached_data
            
            # Obtener información fresca
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                return None
            
            info_dict = symbol_info._asdict()
            
            # Actualizar cache
            self._symbol_info_cache[symbol] = (info_dict, current_time)
            
            return info_dict
            
        except Exception as e:
            self.error.log_error("MT5_SYMBOL_INFO_EXCEPTION", 
                               f"Excepción al obtener info de {symbol}: {str(e)}",
                               {"symbol": symbol, "exception": str(e)})
            return None
    
    def get_market_status(self, symbol: str) -> bool:
        """
        Verifica si el mercado está abierto para un símbolo
        
        Args:
            symbol: Símbolo del instrumento
            
        Returns:
            bool: True si mercado abierto
        """
        symbol_info = self.get_symbol_info(symbol)
        if not symbol_info:
            return False
        
        return symbol_info.get("trade_mode") in [
            mt5.SYMBOL_TRADE_MODE_FULL,
            mt5.SYMBOL_TRADE_MODE_LONGONLY,
            mt5.SYMBOL_TRADE_MODE_SHORTONLY
        ]
    
    # =================================================================
    # MÉTODOS DE UTILIDAD
    # =================================================================
    
    def cleanup(self):
        """Limpia recursos y desconecta"""
        self.logger.log_info("Limpiando MT5Manager...")
        
        self.disconnect()
        self._symbol_info_cache.clear()
        
        self.logger.log_info("MT5Manager limpiado exitosamente")
    
    def __del__(self):
        """Destructor - asegura desconexión"""
        try:
            if hasattr(self, '_is_connected') and self._is_connected:
                self.cleanup()
        except:
            pass  # Ignorar errores en destructor
